#!/usr/bin/env python3
import csv
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


MODEL = os.environ.get("METEO_MODEL", "Fineoffset-WHx080")
LOG_FILE = Path(os.environ.get("METEO_CSV_LOG", "/var/lib/meteo-rtl-sdr/rtl_433.csv"))
STATE_DIR = Path(os.environ.get("METEO_STATE_DIR", "/var/lib/meteo-rtl-sdr/state"))
STATION_ID = os.environ.get("WU_STATION_ID", "")
PASSWORD = os.environ.get("WU_PASSWORD", "")
DRY_RUN = os.environ.get("WU_DRY_RUN", "0") == "1"
MAX_DATA_AGE_SECONDS = int(os.environ.get("MAX_DATA_AGE_SECONDS", "600"))
MAX_FUTURE_SKEW_SECONDS = int(os.environ.get("MAX_FUTURE_SKEW_SECONDS", "60"))


def fail(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def as_float(value, default=None):
    if value in (None, "", "null", "NULL"):
        return default
    try:
        parsed = float(value)
    except ValueError:
        return default
    if math.isnan(parsed) or math.isinf(parsed):
        return default
    return parsed


def in_range(value, minimum, maximum):
    return value is not None and minimum <= value <= maximum


def read_last_record(path: Path, model: str):
    header = None
    last = None

    with path.open(newline="", errors="replace") as handle:
        for row in csv.reader(handle):
            if not row:
                continue
            if row[0] == "time":
                header = row
                continue
            if header is None or len(row) < 4:
                continue
            record = dict(zip(header, row))
            if record.get("model") == model:
                last = record

    return last


def parse_record_epoch(record):
    value = record.get("time")
    if not value:
        return None
    normalized = value.replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(normalized, fmt).timestamp()
        except ValueError:
            continue
    return None


def first_float(record, *names):
    for name in names:
        value = as_float(record.get(name))
        if value is not None:
            return value
    return None


def read_state_float(path: Path, default: float) -> float:
    try:
        return float(path.read_text().strip())
    except (FileNotFoundError, ValueError):
        return default


def write_state_float(path: Path, value: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{value:.6f}\n")


def main() -> int:
    if not LOG_FILE.exists():
        fail(f"CSV log neexistuje: {LOG_FILE}")
    if not STATION_ID or not PASSWORD:
        fail("Chybi WU_STATION_ID nebo WU_PASSWORD")

    record = read_last_record(LOG_FILE, MODEL)
    if not record:
        fail(f"V CSV neni zadny zaznam modelu {MODEL}")

    record_epoch = parse_record_epoch(record)
    if record_epoch is None:
        fail(f"Nelze precist cas mereni: {record.get('time')}")

    age_seconds = int(time.time() - record_epoch)
    if age_seconds > MAX_DATA_AGE_SECONDS:
        fail(f"Data jsou stara {age_seconds}s, neposilam: {record.get('time')}", code=0)
    if age_seconds < -MAX_FUTURE_SKEW_SECONDS:
        fail(f"Data maji cas v budoucnosti ({age_seconds}s), neposilam: {record.get('time')}", code=0)

    temp_c = first_float(record, "temperature_C")
    humidity = first_float(record, "humidity")
    wind_kmh = first_float(record, "wind_avg_km_h")
    gust_kmh = first_float(record, "wind_max_km_h")
    wind_dir = first_float(record, "wind_dir_deg", "direction")
    rain_total_in = first_float(record, "rain_in")

    if not in_range(temp_c, -50, 50):
        fail(f"Nevalidni teplota: {temp_c}")
    if not in_range(humidity, 0, 100):
        fail(f"Nevalidni vlhkost: {humidity}")

    wind_kmh = wind_kmh if in_range(wind_kmh, 0, 200) else 0
    gust_kmh = gust_kmh if in_range(gust_kmh, 0, 200) else 0
    wind_dir = wind_dir if in_range(wind_dir, 0, 360) else 0
    rain_total_in = rain_total_in if in_range(rain_total_in, 0, 40) else 0

    last_rain_path = STATE_DIR / "last_rain_total_in.txt"
    midnight_path = STATE_DIR / "midnight_rain_total_in.txt"
    date_path = STATE_DIR / "rain_date.txt"

    today = time.strftime("%Y-%m-%d")
    if date_path.exists() and date_path.read_text().strip() != today:
        write_state_float(midnight_path, rain_total_in)
        date_path.write_text(today + "\n")
    elif not date_path.exists():
        write_state_float(midnight_path, rain_total_in)
        date_path.write_text(today + "\n")

    previous_rain = read_state_float(last_rain_path, rain_total_in)
    midnight_rain = read_state_float(midnight_path, rain_total_in)

    rain_delta = max(0.0, rain_total_in - previous_rain)
    rain_today = max(0.0, rain_total_in - midnight_rain)
    write_state_float(last_rain_path, rain_total_in)

    params = {
        "ID": STATION_ID,
        "PASSWORD": PASSWORD,
        "dateutc": "now",
        "tempf": round(temp_c * 9 / 5 + 32, 1),
        "humidity": int(round(humidity)),
        "winddir": int(round(wind_dir)),
        "windspeedmph": round(wind_kmh * 0.621371, 2),
        "windgustmph": round(gust_kmh * 0.621371, 2),
        "rainin": round(rain_delta, 4),
        "dailyrainin": round(rain_today, 4),
        "action": "updateraw",
    }

    public_params = dict(params)
    public_params["PASSWORD"] = "REDACTED"
    print(json.dumps(public_params, sort_keys=True))

    if DRY_RUN:
        return 0

    url = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"
    request_url = url + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(request_url, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")
    print(body.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
