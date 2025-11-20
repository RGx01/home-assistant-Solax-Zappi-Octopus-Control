from datetime import datetime, timedelta
import sqlite3
import os

@service
def battery_budget_schedule():
    """
    Build consolidated reserve schedule:
      - dynamic slots between slot_start -> slot_end at interval_min
      - compressed max-reserve: start_charge -> slot_start (wrap-safe)
      - compressed zero-reserve: slot_end -> start_charge (wrap-safe)
      - avg_kwh present on every entry (0 for compressed)
      - cumulative_kwh meaning: energy required at the start of that entry to guarantee supply UNTIL slot_end
    """
from datetime import datetime, timedelta
import sqlite3
import os

@service
def battery_budget_schedule():
    """
    Full battery_budget_schedule (original logic preserved) with a single-slot fallback when
    there is no day with complete coverage of the dynamic window.

    Fallback schedule (when triggered) is a single entry:
      start: "00:01:00"
      end:   "23:59:59"
      avg_kwh: 0
      cumulative_kwh: usable_capacity (from sensor.solax_discharge_capacity usable_capacity attribute)
      reserve_type: "max"
    """

    log.info("Starting battery_budget_schedule computation (compact)")

    # --- Config / inputs ---
    db_path = "/config/home-assistant_v2.db"
    entity_stat_id = "sensor.daily_house_load"
    days = int(float(state.get("input_number.power_stat_avg_days") or 10))
    tolerance_minutes = 2

    default_start = "05:30"
    default_end = "23:30"
    default_interval = 15

    try:
        slot_start_str = state.get("input_select.slot_start") or default_start
        slot_end_str = state.get("input_select.slot_end") or default_end
        interval_min = int(state.get("input_select.slot_interval") or default_interval)
    except Exception:
        slot_start_str, slot_end_str, interval_min = default_start, default_end, default_interval

    inverter_w = 70
    inverter_kw = inverter_w / 1000.0

    # helper to parse times robustly (HH:MM or HH:MM:SS)
    def parse_time_hms(s):
        if not s:
            return None
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(s, fmt).time()
            except Exception:
                continue
        raise ValueError(f"Invalid time format: {s}")

    # --- Normalize slot start/end to HH:MM:SS strings ---
    slot_start_t = parse_time_hms(slot_start_str)
    slot_end_t = parse_time_hms(slot_end_str)

    slot_start = slot_start_t.strftime("%H:%M:%S")
    slot_end = slot_end_t.strftime("%H:%M:%S")

    # --- Build dynamic slots between slot_start -> slot_end ---
    slot_pairs = []
    today = datetime.today().date()
    start_dt = datetime.combine(today, slot_start_t)
    end_dt = datetime.combine(today, slot_end_t)

    # if slot_end <= slot_start we interpret it as next day (support overnight dynamic window)
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)

    delta = timedelta(minutes=interval_min)

    current = start_dt
    while current < end_dt:
        next_slot = current + delta
        if next_slot > end_dt:
            next_slot = end_dt
        slot_pairs.append((current.strftime("%H:%M:%S"), next_slot.strftime("%H:%M:%S")))
        current = next_slot

    log.info(f"Built {len(slot_pairs)} dynamic slots from {slot_start} to {slot_end} @ {interval_min}min")

    # total duration of dynamic window in hours (after handling crossing-midnight)
    total_dynamic_seconds = (end_dt - start_dt).total_seconds()
    total_dynamic_hours = total_dynamic_seconds / 3600.0 if total_dynamic_seconds > 0 else 0.0

    # --- Prepare accumulators for dynamic slots only ---
    n_slots = len(slot_pairs)
    slot_totals_kwh = [0.0] * n_slots
    slot_totals_hours = [0.0] * n_slots
    slot_day_counts = [0] * n_slots
    valid_day_count = 0

    # --- Read history from recorder DB ---
    if not os.path.exists(db_path):
        log.error(f"Recorder DB not found at {db_path}")
        return

    sql = f"""
      SELECT datetime(start_ts, 'unixepoch', 'localtime') AS ts, state
      FROM statistics_short_term s
      JOIN statistics_meta m ON m.id = s.metadata_id
      WHERE m.statistic_id = '{entity_stat_id}'
        AND start_ts >= strftime('%s', date('now', '-{days} days'))
        AND start_ts < strftime('%s', date('now'))
      ORDER BY start_ts ASC
    """

    rows = []
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
    except Exception as e:
        log.error(f"SQL error: {e}")
        return
    finally:
        if 'conn' in locals() and conn:
            conn.close()

    if not rows:
        log.warning("No rows fetched from recorder DB - will consider fallback")
        # We'll still process further to decide fallback; readings_by_day will be empty.

    # --- Group readings by day (local date) ---
    readings_by_day = {}
    for ts_str, state_str in rows:
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            val = float(state_str)
        except Exception:
            continue
        readings_by_day.setdefault(ts.date(), []).append((ts, val))

    # --- Decide whether at least one day fully covers dynamic window ---
    # Full coverage = at least one reading <= (slot_start + tol) and at least one reading >= (slot_end - tol)
    tol = timedelta(minutes=tolerance_minutes)
    has_full_coverage_day = False

    for day, readings in sorted(readings_by_day.items()):
        if len(readings) < 2:
            continue
        readings.sort(key=lambda x: x[0])

        # Build absolute datetimes for this day's window (handle crossing)
        s_dt = datetime.combine(day, slot_start_t)
        e_dt = datetime.combine(day, slot_end_t)
        if e_dt <= s_dt:
            e_dt += timedelta(days=1)

        start_bound = s_dt + tol
        end_bound = e_dt - tol

        start_seen = False
        end_seen = False
        for t, _ in readings:
            if t <= start_bound:
                start_seen = True
            if t >= end_bound:
                end_seen = True
            if start_seen and end_seen:
                break

        if start_seen and end_seen:
            has_full_coverage_day = True
            break

    # If no full-coverage day -> build single-slot fallback (reserve full usable capacity)
    if not has_full_coverage_day:
        usable_capacity_raw = state.get("sensor.solax_discharge_capacity", attribute="usable_capacity")
        try:
            usable_capacity = float(usable_capacity_raw or 0.0)
        except Exception:
            usable_capacity = 0.0

        # If usable_capacity is zero-ish, try getattr style fallback (older scripts)
        if usable_capacity <= 0:
            try:
                usable_capacity = float(state.getattr("sensor.solax_discharge_capacity").get("usable_capacity", 0.0))
            except Exception:
                usable_capacity = usable_capacity or 0.0

        log.warning("Insufficient historical coverage for dynamic slots — emitting single-slot fallback reserving usable capacity")
        reserve_schedule = [
            {
                "start": "00:01:00",
                "end": "23:59:59",
                "avg_kwh": 0.0,
                "cumulative_kwh": round(usable_capacity, 3),
                "reserve_type": "max",
            }
        ]

        total_daily_kwh = round(usable_capacity, 3)
        daily_average_kw = round(usable_capacity / 24.0 if usable_capacity > 0 else 0.0, 3)

        state.set(
            "sensor.battery_budget_reserve",
            total_daily_kwh,
            {
                "reserve_schedule": reserve_schedule,
                "days_used": 0,
                "inverter_overhead_w": inverter_w,
                "slot_interval_min": interval_min,
                "total_hours": 23.983,  # ~00:01 -> 23:59:59
                "daily_average_kw": daily_average_kw,
                "last_run": datetime.now().isoformat(timespec="seconds"),
            }
        )

        log.info("battery_budget_schedule completed (fallback single-slot)")
        return

    # --- If we reach here, we have at least one full coverage day -> proceed with original per-slot logic ---
    # --- For each day compute per-slot delta for dynamic slots ---
    for day, readings in sorted(readings_by_day.items()):
        if len(readings) < 2:
            continue
        readings.sort(key=lambda x: x[0])

        # Build absolute datetimes for slots for this day; note dynamic window may cross midnight
        # Determine base for dynamic window: start_dt_day and end_dt_day adjusted for crossing midnight
        s_dt = datetime.combine(day, slot_start_t)
        e_dt = datetime.combine(day, slot_end_t)
        if e_dt <= s_dt:
            e_dt += timedelta(days=1)

        # filter readings that fall within a reasonable window: from (s_dt - tolerance) to (e_dt + tolerance)
        window_start = s_dt - tol
        window_end = e_dt + tol

        # pyscript-safe version (no generator expressions)
        has_relevant = False
        for t, _ in readings:
            if window_start <= t <= window_end:
                has_relevant = True
                break

        if not has_relevant:
            # Not enough info for that day
            continue

        valid_day_count += 1

        for i, (slot_s, slot_e) in enumerate(slot_pairs):
            # slot_s and slot_e are strings "HH:MM:SS" relative to the dynamic window start day
            slot_start_dt = datetime.combine(day, datetime.strptime(slot_s, "%H:%M:%S").time())
            slot_end_dt = datetime.combine(day, datetime.strptime(slot_e, "%H:%M:%S").time())
            # if slot_end crosses into next day, add a day
            if slot_end_dt <= slot_start_dt:
                slot_end_dt += timedelta(days=1)

            # find reading near slot_start (within tolerance) or the first reading before slot_end
            start_val = None
            start_time_found = None
            min_diff = timedelta.max
            for t, v in readings:
                diff = abs(t - slot_start_dt)
                if diff <= tol and diff < min_diff:
                    start_val, start_time_found = v, t
                    min_diff = diff
            if start_val is None:
                # fallback: first reading before slot_end
                for t, v in readings:
                    if t <= slot_end_dt:
                        start_val, start_time_found = v, t
                        break

            # find reading near slot_end (within tolerance) or the last reading <= slot_end
            end_val = None
            end_time_found = None
            min_diff = timedelta.max
            for t, v in readings:
                diff = abs(t - slot_end_dt)
                if diff <= tol and diff < min_diff:
                    end_val, end_time_found = v, t
                    min_diff = diff
            if end_val is None:
                for t, v in reversed(readings):
                    if t <= slot_end_dt:
                        end_val, end_time_found = v, t
                        break

            if start_val is not None and end_val is not None and end_time_found > start_time_found:
                delta_kwh = max(0.0, end_val - start_val)
                delta_hours = (end_time_found - start_time_found).total_seconds() / 3600.0
                effective_delta_kwh = delta_kwh + (inverter_kw * delta_hours)

                slot_totals_kwh[i] += effective_delta_kwh
                slot_totals_hours[i] += delta_hours
                slot_day_counts[i] += 1

    if valid_day_count == 0:
        # Defensive: if somehow no valid days remained, fall back (should be unlikely since we checked full coverage earlier)
        usable_capacity_raw = state.get("sensor.solax_discharge_capacity", attribute="usable_capacity")
        try:
            usable_capacity = float(usable_capacity_raw or 0.0)
        except Exception:
            usable_capacity = 0.0
        log.warning("No valid days after per-day processing — falling back to single-slot reserve")
        reserve_schedule = [
            {
                "start": "00:01:00",
                "end": "23:59:59",
                "avg_kwh": 0.0,
                "cumulative_kwh": round(usable_capacity, 3),
                "reserve_type": "max",
            }
        ]
        total_daily_kwh = round(usable_capacity, 3)
        daily_average_kw = round(usable_capacity / 24.0 if usable_capacity > 0 else 0.0, 3)

        state.set(
            "sensor.battery_budget_reserve",
            total_daily_kwh,
            {
                "reserve_schedule": reserve_schedule,
                "days_used": 0,
                "inverter_overhead_w": inverter_w,
                "slot_interval_min": interval_min,
                "total_hours": 23.983,
                "daily_average_kw": daily_average_kw,
                "last_run": datetime.now().isoformat(timespec="seconds"),
            }
        )

        log.info("battery_budget_schedule completed (fallback single-slot)")
        return

    # --- Compute avg_kwh per dynamic slot ---
    avg_kwh_per_slot = [
        round(slot_totals_kwh[i] / slot_day_counts[i], 3) if slot_day_counts[i] > 0 else 0.0
        for i in range(n_slots)
    ]

    # --- Compute cumulative_kwh for dynamic slots (required until slot_end) ---
    cumulative_per_start = {}
    rem = sum(avg_kwh_per_slot)
    for i, (s, _) in enumerate(slot_pairs):
        cumulative_per_start[s] = round(rem, 3)
        rem -= avg_kwh_per_slot[i]
    # after final dynamic slot cumulative -> 0 (implicitly)

    total_daily_kwh = round(sum(avg_kwh_per_slot), 3)

    if total_dynamic_hours > 0:
        daily_average_kw = round(total_daily_kwh / total_dynamic_hours, 3)
    else:
        daily_average_kw = 0.0

    # --- Parse solax start_charge time ---
    start_charge_raw = state.get("input_datetime.solax_battery_start_charge_time")
    if start_charge_raw:
        try:
            start_charge_t = parse_time_hms(start_charge_raw)
            start_charge = start_charge_t.strftime("%H:%M:%S")
        except Exception:
            # fallback parse as HH:MM
            start_charge = parse_time_hms(start_charge_raw).strftime("%H:%M:%S")
    else:
        start_charge = "00:00:00"
        start_charge_t = parse_time_hms(start_charge)

    # --- Helpers for schedule building ---
    def make_entry(start_s, end_s, avg_kwh, cumulative_kwh, rtype):
        return {
            "start": start_s,
            "end": end_s,
            "avg_kwh": round(avg_kwh, 3),
            "cumulative_kwh": round(cumulative_kwh, 3),
            "reserve_type": rtype,  # "max" | "dynamic" | "zero"
        }

    # add a possibly-wrapping compressed range. If start <= end => single range, else split into two ranges.
    def add_compressed_range(schedule_list, start_s, end_s, avg_kwh, cumulative_kwh, rtype):
        if start_s <= end_s:
            schedule_list.append(make_entry(start_s, end_s, avg_kwh, cumulative_kwh, rtype))
        else:
            # split: start -> 23:59:59 and 00:00:00 -> end
            schedule_list.append(make_entry(start_s, "23:59:59", avg_kwh, cumulative_kwh, rtype))
            schedule_list.append(make_entry("00:00:00", end_s, avg_kwh, cumulative_kwh, rtype))

    # --- Build final reserve_schedule with compressed zero/max and detailed dynamic slots ---
    reserve_schedule = []

    # 1) max reserve: start_charge -> slot_start  (compressed, may wrap)
    # avg_kwh = 0 for compressed, cumulative = total_daily_kwh
    add_compressed_range(reserve_schedule, start_charge, slot_start, 0.0, total_daily_kwh, "max")

    # 2) dynamic slots: slot_start -> slot_end (these are the per-interval slots)
    # add each dynamic slot in order
    for i, (s, e) in enumerate(slot_pairs):
        cum = cumulative_per_start.get(s, 0.0)
        avg = avg_kwh_per_slot[i]
        reserve_schedule.append(make_entry(s, e, avg, cum, "dynamic"))

    # 3) zero reserve: slot_end -> start_charge (compressed, may wrap)
    add_compressed_range(reserve_schedule, slot_end, start_charge, 0.0, 0.0, "zero")

    # --- Publish compact sensor (only single consolidated schedule payload) ---
    state.set(
        "sensor.battery_budget_reserve",
        total_daily_kwh,
        {
            "reserve_schedule": reserve_schedule,
            "days_used": valid_day_count,
            "inverter_overhead_w": inverter_w,
            "slot_interval_min": interval_min,
            "total_hours": round(total_dynamic_hours, 3),
            "daily_average_kw": daily_average_kw,
            "last_run": datetime.now().isoformat(timespec="seconds"),
        }
    )

    log.info("battery_budget_schedule completed successfully (compact schedule)")
