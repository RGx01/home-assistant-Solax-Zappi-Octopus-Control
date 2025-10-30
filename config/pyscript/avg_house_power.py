def get_float(entity_id, default=0.0):
    try:
        return float(state.get(entity_id))
    except (TypeError, ValueError):
        return default

def get_int(entity_id, default=0):
    return int(get_float(entity_id, default))

@service
def energy_avg_query():
    """Dynamically compute average power from statistics table."""
    import sqlite3

    db_path = "/config/home-assistant_v2.db"

    days = get_int("input_number.power_stat_avg_days")
    typical_kw = get_float("input_number.typical_house_power")
    start_time = state.get("input_datetime.power_stat_start_time") or "00:00:00"
    end_time = state.get("input_datetime.power_stat_end_time") or "23:59:59"

    sql = f"""
    WITH params AS (
      SELECT {days} AS days,
             '{start_time}' AS start_time,
             '{end_time}' AS end_time
    ),
    hourly AS (
      SELECT
        date(datetime(start_ts, 'unixepoch', 'localtime')) AS day,
        strftime('%H:%M:%S', datetime(start_ts, 'unixepoch', 'localtime')) AS hour,
        state
      FROM statistics s
      JOIN statistics_meta m ON m.id = s.metadata_id
      WHERE m.statistic_id = 'sensor.daily_house_load'
        AND start_ts >= strftime('%s', date('now', '-' || (SELECT days FROM params) || ' days', 'localtime'))
        AND start_ts < strftime('%s', date('now', 'localtime'))
    ),
    daily AS (
      SELECT
        day,
        MAX(state) FILTER (WHERE hour <= (SELECT end_time FROM params)) AS end_val,
        MAX(state) FILTER (WHERE hour <= (SELECT start_time FROM params)) AS start_val
      FROM hourly
      GROUP BY day
      HAVING day < date('now', 'localtime')
      ORDER BY day DESC
      LIMIT (SELECT days FROM params)
    ),
    daily_calc AS (
      SELECT
        day,
        ROUND((end_val - start_val) /
          ((strftime('%H', (SELECT end_time FROM params)) -
            strftime('%H', (SELECT start_time FROM params)))), 3) AS kW
      FROM daily
      WHERE end_val IS NOT NULL AND start_val IS NOT NULL
    )
    SELECT COALESCE(ROUND(AVG(kW), 3), {typical_kw}) AS avg_kw
    FROM daily_calc;
    """

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchone()[0]
    except Exception as e:
        log.error(f"SQL error: {e}")
        state.set("sensor.average_house_power", "unavailable")
        return
    finally:
        if conn:
            conn.close()

    # Publish result
    state.set(
        "sensor.average_house_power",
        result,
        {
            "unit_of_measurement": "kW",
            "state_class": "measurement",
            "device_class": "power",
            "friendly_name": "Average House Power (History Driven)",
            "icon": "mdi:flash",
        },
    )
    log.info(f"Updated sensor.average_house_power: {result} kW")


@time_trigger("startup")
def init_energy_avg_sensor():
    """Ensure the sensor exists on startup."""
    state.set(
        "sensor.average_house_power",
        "unavailable",
        {
            "unit_of_measurement": "kW",
            "state_class": "measurement",
            "device_class": "power",
            "friendly_name": "Average House Power (History Driven)",
            "icon": "mdi:flash",
        },
    )
    log.info("Initialized sensor.average_house_power on startup")
