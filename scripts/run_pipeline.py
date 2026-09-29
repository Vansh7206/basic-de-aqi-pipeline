import logging

import clean_aqi
import fetch_aqi
import load_aqi
from config import CITIES, LOG_DIR

LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def check_row(row):
    for key in ("city", "observed_at", "us_aqi"):
        if row.get(key) is None:
            raise ValueError(f"Missing value: {key}")
    if not 0 <= row["us_aqi"] <= 500:
        raise ValueError(f"Unrealistic AQI: {row['us_aqi']}")
    for key in ("pm2_5", "pm10"):
        if row[key] is not None and row[key] < 0:
            raise ValueError(f"Negative {key}: {row[key]}")


def run():
    logging.info("Pipeline started")
    try:
        rows = []
        for city, coords in CITIES.items():
            try:
                row = fetch_aqi.fetch_city(city, coords)
                check_row(row)
                rows.append(row)
                logging.info("Fetched OK: %s, AQI %s", city, row["us_aqi"])
            except Exception as e:
                logging.error("City FAILED: %s - %s", city, e)

        if not rows:
            raise RuntimeError("No city returned valid data")

        fetch_aqi.save_csv(rows)
        logging.info("Saved CSV (%d cities)", len(rows))

        load_aqi.create_database_if_missing()
        load_aqi.load_csv_files()
        logging.info("Loaded into raw_aqi")

        clean_aqi.clean()
        logging.info("Rebuilt clean_aqi")

        if len(rows) < len(CITIES):
            logging.warning("Finished with %d of %d cities", len(rows), len(CITIES))
        else:
            logging.info("Pipeline finished OK")
    except Exception:
        logging.exception("Pipeline FAILED")
        raise


if __name__ == "__main__":
    run()