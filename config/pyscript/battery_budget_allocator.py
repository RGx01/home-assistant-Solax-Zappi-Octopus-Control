# battery_budget_allocator.py
# Pyscript version with: single-active-run protection, debounce, dev cleanup, diagnostics, and dynamic icon

import uuid
from datetime import datetime, timedelta

# --- Dev-mode: cancel lingering tasks on reload ---
try:
    if _debounce_task is not None:
        try:
            _debounce_task.cancel()
            log.info("Dev reload: cancelled previous _debounce_task")
        except Exception:
            log.warning("Dev reload: failed to cancel previous _debounce_task")
except NameError:
    _debounce_task = None

try:
    if _running_task is not None:
        try:
            _running_task.cancel()
            log.info("Dev reload: cancelled previous _running_task")
        except Exception:
            log.warning("Dev reload: failed to cancel previous _running_task")
except NameError:
    _running_task = None

# --- Globals ---
_running_task = None
_debounce_task = None
_active_run_id = None


# ---------------------------------------------------------
#  Battery level → icon mapper
# ---------------------------------------------------------
def battery_icon(b_soc: float) -> str:
    if b_soc > 95:
        return "mdi:battery"
    elif b_soc > 89:
        return "mdi:battery-90"
    elif b_soc > 79:
        return "mdi:battery-80"
    elif b_soc > 69:
        return "mdi:battery-70"
    elif b_soc > 59:
        return "mdi:battery-60"
    elif b_soc > 49:
        return "mdi:battery-50"
    elif b_soc > 39:
        return "mdi:battery-40"
    elif b_soc > 29:
        return "mdi:battery-30"
    elif b_soc > 19:
        return "mdi:battery-20"
    elif b_soc > 9:
        return "mdi:battery-10"
    else:
        return "mdi:battery-outline"


# ---------------------------------------------------------
#  Debounce wrapper
# ---------------------------------------------------------
@state_trigger("input_number.additional_reserve_soc, "
               "input_number.hours_of_reserve_energy, "
               "input_number.typical_house_power")
def allocator_trigger():
    """Debounce wrapper: fire allocator after short delay."""
    global _debounce_task
    if _debounce_task is not None:
        try:
            _debounce_task.cancel()
            log.info("Debounce: cancelled previous _debounce_task due to trigger")
        except Exception:
            log.warning("Debounce: failed to cancel previous _debounce_task")

    _debounce_task = task.create(_debounce_run)


async def _debounce_run():
    await task.sleep(0.3)
    run_id = uuid.uuid4().hex[:8]
    log.info(f"Debounce: running allocator after delay (run_id={run_id})")
    battery_budget_allocator(run_id=run_id)


# ---------------------------------------------------------
#  Main Allocator
# ---------------------------------------------------------
@service
def battery_budget_allocator(run_id: str = None):
    global _running_task, _active_run_id

    if run_id is None:
        run_id = uuid.uuid4().hex[:8]

    # Ensure only one active run executes at a time
    if _active_run_id is not None:
        log.info(f"Allocator [{run_id}]: exiting because run [{_active_run_id}] is still active")
        return

    _active_run_id = run_id
    log.info(f"Allocator [{run_id}]: attempting to start run")

    try:
        # Cancel any previously scheduled run
        if _running_task is not None:
            try:
                _running_task.cancel()
                log.info(f"Allocator [{run_id}]: cancelled previous scheduled run")
            except Exception:
                log.warning(f"Allocator [{run_id}]: failed to cancel previous scheduled run")
            _running_task = None

        # Ensure schedule exists
        if "sensor.battery_budget_reserve" not in state.names():
            log.warning(f"Allocator [{run_id}]: sensor.battery_budget_reserve missing - aborting")
            return

        attrs = state.getattr("sensor.battery_budget_reserve") or {}
        schedule = attrs.get("reserve_schedule", [])
        if not schedule:
            log.warning(f"Allocator [{run_id}]: reserve_schedule empty - aborting")
            return

        now = datetime.now()
        now_str = now.strftime("%H:%M:%S")

        def time_in_range(start_s, end_s, now_s):
            if start_s <= end_s:
                return start_s <= now_s < end_s
            return now_s >= start_s or now_s < end_s

        # Find current entry
        current_entry = None
        for entry in schedule:
            if time_in_range(entry.get("start"), entry.get("end"), now_str):
                current_entry = entry
                break

        if current_entry is None:
            last_before = None
            for entry in schedule:
                if entry.get("start") <= now_str:
                    last_before = entry
            current_entry = last_before or schedule[0]

        current_slot = current_entry.get("start")
        reserve_kwh = float(current_entry.get("cumulative_kwh", 0.0))

        # Battery properties
        batt_usable = float(state.getattr("sensor.solax_discharge_capacity").get("usable_capacity", 10))
        min_soc = float(state.get("input_number.solax_default_discharge_limit_soc") or 10)
        usable_percent = max(0.0, 100.0 - min_soc)

        # User inputs
        additional_pct = float(state.get("input_number.additional_reserve_soc") or 0)
        hours_buffer = float(state.get("input_number.hours_of_reserve_energy") or 0)
        typical_kw = float(state.get("input_number.typical_house_power") or 0)

        buffer_kwh = (hours_buffer * typical_kw) + (batt_usable * additional_pct / 100)

        # Convert reserve → SoC %
        if batt_usable > 0 and usable_percent > 0:
            required_soc = min_soc + (reserve_kwh / batt_usable) * usable_percent
            target_soc = min_soc + ((reserve_kwh + buffer_kwh) / batt_usable) * usable_percent
        else:
            required_soc = min_soc
            target_soc = min_soc

        required_soc = max(min(required_soc, 100.0), min_soc)
        target_soc = max(min(target_soc, 100.0), min_soc)

        # Diagnostics: compute remaining kWh above min_soc using ACTUAL SoC
        current_soc = float(state.get("sensor.solax_local_battery_soc") or 0)

        # Clamp SoC to safe range
        current_soc = max(min(current_soc, 100.0), min_soc)

        if usable_percent > 0:
            # Compute kWh between min_soc and current_soc
            remaining_frac = (current_soc - min_soc) / usable_percent
            remaining_kwh_at_current_soc = max(0.0, min(remaining_frac * batt_usable, batt_usable))
        else:
            remaining_kwh_at_current_soc = 0.0


        if batt_usable > 0 and usable_percent > 0:
            additional_soc_abs = (buffer_kwh / batt_usable) * usable_percent
            additional_pct_of_usable = (buffer_kwh / batt_usable) * 100.0
        else:
            additional_soc_abs = 0.0
            additional_pct_of_usable = 0.0

        delta = current_soc - target_soc
        deficit_val = round(delta, 0) if delta < 0 else ""

        # Determine next run time
        next_run = None
        for entry in schedule:
            s = entry.get("start")
            t = now.replace(hour=int(s[0:2]), minute=int(s[3:5]), second=int(s[6:8]))
            if t > now:
                next_run = t
                break
        if next_run is None:
            first = schedule[0].get("start")
            next_run = now.replace(
                hour=int(first[0:2]), minute=int(first[3:5]), second=int(first[6:8])
            ) + timedelta(days=1)

        delay_seconds = (next_run - now).total_seconds()

        # --- Dynamic icon ---
        icon = battery_icon(target_soc)

        # --- Update reserve SoC sensor ---
        state.set(
            "sensor.battery_budget_reserve_soc",
            int(round(target_soc)),
            {
                "current_slot": current_slot,
                "reserve_kwh": round(reserve_kwh, 3),
                "additional_pct_reserve": additional_pct,
                "additional_reserve_soc": round(additional_soc_abs, 0),
                "additional_reserve_pct_of_usable": round(additional_pct_of_usable, 0),
                "reserve_soc": round(required_soc, 0),
                "deficite": deficit_val,
                "batt_usable_kwh": batt_usable,
                "usable_percent": round(usable_percent, 2),
                "remaining_kwh_at_current_soc": round(remaining_kwh_at_current_soc, 3),
                "min_soc": min_soc,
                "next_run": next_run.strftime("%H:%M:%S"),
                "note": "Dynamic SoC based on consolidated schedule",
                "unit_of_measurement": "%",
                "device_class": "battery",
                "state_class": "measurement",
                "icon": icon,
                "unique_id": "battery_budget_reserve_soc",
                "friendly_name": "Battery Budget Reserve SoC"
            }
        )

        # --- Update reserve kWh sensor ---
        total_reserve = reserve_kwh + buffer_kwh
        state.set(
            "sensor.battery_budget_reserve_kwh",
            round(total_reserve, 2),
            {
                "current_slot": current_slot,
                "reserve_kwh": round(reserve_kwh, 2),
                "additional_reserve_kwh": round(buffer_kwh, 2),
                "unit_of_measurement": "kWh",
                "device_class": "energy",
                "state_class": "measurement",
                "icon": "mdi:flash",
                "unique_id": "battery_budget_reserve_kwh",
                "friendly_name": "Battery Budget Reserve kWh"
            }
        )

        log.info(f"[allocator {run_id}] Slot={current_slot}, reserve={reserve_kwh:.3f} kWh, buffer={buffer_kwh:.3f} kWh")
        log.info(f"[allocator {run_id}] Target SoC={target_soc:.1f}% (required {required_soc:.1f}%) Next at {next_run}")

        # Schedule next run
        _running_task = task.create(schedule_next_run, delay_seconds, run_id)

    finally:
        log.info(f"Allocator [{run_id}]: finishing and clearing active_run_id")
        _active_run_id = None


# ---------------------------------------------------------
#  Async scheduler helper
# ---------------------------------------------------------
async def schedule_next_run(delay_seconds, run_id=None):
    await task.sleep(delay_seconds)
    if run_id is None:
        run_id = uuid.uuid4().hex[:8]
    log.info(f"Scheduled next allocator run (run_id={run_id})")
    battery_budget_allocator(run_id=run_id)
