"""
battery_budget_schedule v8.0.0
--------------------------------
Purpose:
Build a consolidated battery reserve schedule with wrap-around support.

Requirements:
1. Compute dynamic slots based on configured start/end times and interval.
2. Accumulate historical house load kWh per slot.
3. Calculate average kWh per slot and cumulative kWh remaining per start of slot.
4. Handle wrap-around slots that cross midnight.
5. If battery charging window (start/stop) impinges on any dynamic slots:
    - Discard dynamic slots.
    - Generate a single max-reserve slot from 00:00:00 to 23:59:59.
    - Preserve cumulative_kwh as total daily kWh.
    - Log a warning.
6. Only charge outside dynamic slots; dynamic slots represent actual house load without battery charging inflating energy usage.
7. Save final schedule to state with relevant metadata.
"""

from datetime import datetime, timedelta
import sqlite3
import os

@service
def battery_budget_schedule():
    """
    Build consolidated battery reserve schedule with wrap-around support.
    """

    log.info("Starting battery_budget_schedule computation (v8.0.0, wrap-aware)")

    # --- Config / inputs ---
    db_path = "/config/home-assistant_v2.db"
    entity_stat_id = "sensor.daily_house_load"
    days = int(float(state.get("input_number.power_stat_avg_days") or 10))
    tolerance_minutes = 2

    default_start = "05:30"
    default_end = "23:30"
    default_interval = 15

    # Read slot configuration
    try:
        slot_start_str = state.get("input_select.slot_start") or default_start
        slot_end_str = state.get("input_select.slot_end") or default_end
        interval_min = int(state.get("input_select.slot_interval") or default_interval)
    except Exception:
        slot_start_str, slot_end_str, interval_min = default_start, default_end, default_interval

    inverter_w = 70
    inverter_kw = inverter_w / 1000.0

    # --- Helper to parse time ---
    def parse_time_hms(s):
        if not s:
            return None
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(s, fmt).time()
            except Exception:
                continue
        raise ValueError(f"Invalid time format: {s}")

    # --- Build dynamic slots ---
    slot_start_t = parse_time_hms(slot_start_str)
    slot_end_t = parse_time_hms(slot_end_str)

    slot_pairs = []
    today = datetime.today().date()
    start_dt = datetime.combine(today, slot_start_t)
    end_dt = datetime.combine(today, slot_end_t)
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

    log.info(f"Built {len(slot_pairs)} dynamic slots from {slot_start_t} to {slot_end_t} @ {interval_min}min")

    total_dynamic_seconds = (end_dt - start_dt).total_seconds()
    total_dynamic_hours = total_dynamic_seconds / 3600.0 if total_dynamic_seconds > 0 else 0.0

    # --- Read history ---
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

    readings_by_day = {}
    for ts_str, state_str in rows:
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            val = float(state_str)
        except Exception:
            continue
        readings_by_day.setdefault(ts.date(), []).append((ts, val))

    tol = timedelta(minutes=tolerance_minutes)
    has_full_coverage_day = False
    for day, readings in sorted(readings_by_day.items()):
        if len(readings) < 2:
            continue
        readings.sort(key=lambda x: x[0])
        s_dt_day = datetime.combine(day, slot_start_t)
        e_dt_day = datetime.combine(day, slot_end_t)
        if e_dt_day <= s_dt_day:
            e_dt_day += timedelta(days=1)

        start_bound = s_dt_day + tol
        end_bound = e_dt_day - tol

        start_seen = end_seen = False
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

    # --- Parse start/stop charge ---
    start_charge_raw = state.get("input_datetime.solax_battery_start_charge_time")
    stop_charge_raw = state.get("input_datetime.solax_battery_stop_charge_time")

    if start_charge_raw and stop_charge_raw:
        start_charge_t = parse_time_hms(start_charge_raw)
        stop_charge_t = parse_time_hms(stop_charge_raw)
    else:
        start_charge_t = stop_charge_t = parse_time_hms("00:00:00")

    # --- Check for charging window overlap ---
    impinges_dynamic_slots = False
    for s, e in slot_pairs:
        slot_s_dt = datetime.combine(today, datetime.strptime(s, "%H:%M:%S").time())
        slot_e_dt = datetime.combine(today, datetime.strptime(e, "%H:%M:%S").time())
        if slot_e_dt <= slot_s_dt:
            slot_e_dt += timedelta(days=1)
        charge_s_dt = datetime.combine(today, start_charge_t)
        charge_e_dt = datetime.combine(today, stop_charge_t)
        if charge_e_dt <= charge_s_dt:
            charge_e_dt += timedelta(days=1)

        if (charge_s_dt < slot_e_dt and charge_e_dt > slot_s_dt):
            impinges_dynamic_slots = True
            break

    # --- Accumulate per slot (or handle max-reserve override) ---
    n_slots = len(slot_pairs)
    slot_totals_kwh = [0.0] * n_slots
    slot_totals_hours = [0.0] * n_slots
    slot_day_counts = [0] * n_slots
    valid_day_count = 0

    if impinges_dynamic_slots:
        log.warning("Battery charging window overlaps dynamic slots: overriding with single max-reserve slot")
        total_daily_kwh = 0.0
        for day, readings in readings_by_day.items():
            for _, v in readings:
                total_daily_kwh += v
        total_daily_kwh = round(total_daily_kwh, 3)
        reserve_schedule = [dict(
            start="00:00:00",
            end="23:59:59",
            avg_kwh=0.0,
            cumulative_kwh=total_daily_kwh,
            reserve_type="max"
        )]
        daily_average_kw = round(total_daily_kwh / total_dynamic_hours, 3) if total_dynamic_hours > 0 else 0.0
    else:
        # --- Original accumulation logic ---
        for day, readings in sorted(readings_by_day.items()):
            if len(readings) < 2:
                continue
            readings.sort(key=lambda x: x[0])
            s_dt_day = datetime.combine(day, slot_start_t)
            e_dt_day = datetime.combine(day, slot_end_t)
            if e_dt_day <= s_dt_day:
                e_dt_day += timedelta(days=1)

            window_start = s_dt_day - tol
            window_end = e_dt_day + tol

            has_relevant = False
            for t, _ in readings:
                if window_start <= t <= window_end:
                    has_relevant = True
                    break
            if not has_relevant:
                continue
            valid_day_count += 1

            for i, (slot_s, slot_e) in enumerate(slot_pairs):
                slot_s_dt = datetime.combine(day, datetime.strptime(slot_s, "%H:%M:%S").time())
                slot_e_dt = datetime.combine(day, datetime.strptime(slot_e, "%H:%M:%S").time())
                if slot_e_dt <= slot_s_dt:
                    slot_e_dt += timedelta(days=1)

                start_val = None
                for t, v in readings:
                    if t <= slot_s_dt:
                        start_val = v

                end_val = None
                for t, v in reversed(readings):
                    if t <= slot_e_dt:
                        end_val = v
                        break

                if start_val is not None and end_val is not None:
                    delta_hours = (slot_e_dt - slot_s_dt).total_seconds() / 3600.0
                    delta_kwh = max(0.0, end_val - start_val) + inverter_kw * delta_hours
                    slot_totals_kwh[i] += delta_kwh
                    slot_totals_hours[i] += delta_hours
                    slot_day_counts[i] += 1

        # --- Compute averages ---
        avg_kwh_per_slot = [round(slot_totals_kwh[i] / slot_day_counts[i], 3) if slot_day_counts[i] > 0 else 0.0 for i in range(n_slots)]
        rem = sum(avg_kwh_per_slot)
        cumulative_per_start = {}
        for i, (s, _) in enumerate(slot_pairs):
            cumulative_per_start[s] = round(rem, 3)
            rem -= avg_kwh_per_slot[i]

        total_daily_kwh = round(sum(avg_kwh_per_slot), 3)
        daily_average_kw = round(total_daily_kwh / total_dynamic_hours, 3) if total_dynamic_hours > 0 else 0.0

        # --- Build final reserve_schedule ---
        reserve_schedule = []

        def make_entry(start_s, end_s, avg_kwh, cumulative_kwh, rtype):
            return {
                "start": start_s,
                "end": end_s,
                "avg_kwh": round(avg_kwh, 3),
                "cumulative_kwh": round(cumulative_kwh, 3),
                "reserve_type": rtype,
            }

        def add_wrap_range(schedule_list, start_s, end_s, avg_kwh, cumulative_kwh, rtype):
            start_dt = datetime.strptime(start_s, "%H:%M:%S")
            end_dt = datetime.strptime(end_s, "%H:%M:%S")
            if start_dt < end_dt:
                schedule_list.append(make_entry(start_s, end_s, avg_kwh, cumulative_kwh, rtype))
            elif start_dt > end_dt:
                schedule_list.append(make_entry(start_s, "23:59:59", avg_kwh, cumulative_kwh, rtype))
                schedule_list.append(make_entry("00:00:00", end_s, avg_kwh, cumulative_kwh, rtype))

        add_wrap_range(reserve_schedule, start_charge_t.strftime("%H:%M:%S"),
                       slot_pairs[0][0], 0.0, total_daily_kwh, "max")

        for i, (s, e) in enumerate(slot_pairs):
            cum = cumulative_per_start.get(s, 0.0)
            avg = avg_kwh_per_slot[i]
            reserve_schedule.append(make_entry(s, e, avg, cum, "dynamic"))

        add_wrap_range(reserve_schedule, slot_pairs[-1][1],
                       start_charge_t.strftime("%H:%M:%S"), 0.0, 0.0, "zero")

        reserve_schedule.sort(key=lambda x: datetime.strptime(x["start"], "%H:%M:%S"))

    # --- Save to state ---
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

    log.info("battery_budget_schedule completed successfully (v8.0.0)")
