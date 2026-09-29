import csv
from datetime import datetime

import requests

from config import CITIES, RAW_DIR

URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
FIELDS = [
    "us_aqi", "pm2_5", "pm10", "carbon_monoxide",
    "nitrogen_dioxide", "sulphur_dioxide", "ozone",
]
CSV_COLUMNS = ["city", "observed_at", *FIELDS, "fetched_at"]


def fetch_city(city, coords):
    params = {
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "current": ",".join(FIELDS),
        "timezone": "Asia/Kolkata",
    }
    response = requests.get(URL, params=params, timeout=30)
    response.raise_for_status()
    current = response.json()["current"]

    row = {"city": city, "observed_at": current["time"]}
    for field in FIELDS:
        row[field] = current.get(field)
    row["fetched_at"] = datetime.now().isoformat(timespec="seconds")
    return row


def fetch_all():
    rows = []
    for city, coords in CITIES.items():
        try:
            rows.append(fetch_city(city, coords))
        except Exception as e:
            print(f"FAILED {city}: {e}")
    return rows


def save_csv(rows):
    RAW_DIR.mkdir(exist_ok=True)
    filename = RAW_DIR / f"aqi_{datetime.now():%Y-%m-%d}.csv"
    file_exists = filename.exists()

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

    return filename


if __name__ == "__main__":
    rows = fetch_all()
    for row in rows:
        print(row)
    if rows:
        print("Saved to:", save_csv(rows))