# India AQI Pipeline

A basic data engineering project that collects air quality data for **Mumbai, Delhi and Bengaluru** every hour, stores it raw in PostgreSQL, cleans it with SQL, and shows it on a Streamlit dashboard.

Built to learn the full flow of a pipeline: **Get → Store → Load → Clean → Automate → Check → Serve**.

<!-- Add a dashboard screenshot here: ![Dashboard](docs/dashboard.png) -->

## Pipeline

```
Open-Meteo API → raw CSV files → raw_aqi (PostgreSQL) → clean_aqi (PostgreSQL) → Streamlit dashboard
     Get             Store              Load                     Clean                    Serve
                                                                   ↑
                                     Runs every hour with data checks and a log file
```

## Tech stack

Python · PostgreSQL · SQL · Streamlit · pandas · SQLAlchemy

Data source: [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) (free, no API key).

## What it does

1. **Get**: calls the API for each city and reads US AQI, PM2.5, PM10, CO, NO2, SO2 and ozone.
2. **Store**: saves every fetch as a raw CSV in `raw/`, one file per day.
3. **Load**: inserts the CSV rows into the `raw_aqi` table, untouched.
4. **Clean**: builds `clean_aqi` with duplicates removed, rows without an AQI dropped, and an `aqi_category` column added.
5. **Check**: validates each reading and writes every run to `logs/pipeline.log`.
6. **Automate**: `scheduler.py` runs the whole pipeline every hour.
7. **Serve**: the dashboard reads `clean_aqi` and shows the latest AQI, trends and pollutant levels.

## Tables

| Table | Purpose |
|---|---|
| `raw_aqi` | Everything as received, duplicates included |
| `clean_aqi` | One row per city per observation time, plus `aqi_category` |

**Cleaning rules**

- Keep one row per (`city`, `observed_at`), the most recently fetched
- Drop rows where `us_aqi` is missing
- Add a category from the US AQI:

| US AQI | Category |
|---|---|
| 0 - 50 | Good |
| 51 - 100 | Moderate |
| 101 - 150 | Unhealthy for Sensitive Groups |
| 151 - 200 | Unhealthy |
| 201 - 300 | Very Unhealthy |
| 301+ | Hazardous |

## Data checks

A city's reading is rejected and logged if:

- `city`, `observed_at` or `us_aqi` is missing
- `us_aqi` is outside 0 - 500
- `pm2_5` or `pm10` is negative

If one city fails, the other cities are still saved and loaded, and the log records which one failed.

## Project structure

```
india-aqi-pipeline/
├── scripts/
│   ├── config.py          # cities, paths, database settings
│   ├── fetch_aqi.py       # get data from the API, save raw CSVs
│   ├── load_aqi.py        # load CSVs into raw_aqi
│   ├── clean_aqi.py       # build clean_aqi
│   ├── run_pipeline.py    # run all steps with checks and logging
│   └── scheduler.py       # run the pipeline every hour
├── dashboard/
│   └── dashboard.py       # Streamlit dashboard
├── logs/                  # pipeline.log (not committed)
├── raw/                   # raw CSV files (not committed)
├── .env                   # database password (not committed)
└── .gitignore
```

## Setup

Requirements: Python 3.10+ and PostgreSQL.

```
git clone https://github.com/Vansh7206/india-aqi-pipeline.git
cd india-aqi-pipeline
pip install requests psycopg2-binary python-dotenv streamlit pandas sqlalchemy
```

Create a `.env` file in the project root:

```
DB_PASSWORD=your_postgres_password
```

The database `aqi_db` is created automatically on the first run.

## Run

Run the pipeline once:

```
python scripts/run_pipeline.py
```

Run it every hour (keep the terminal open):

```
python scripts/scheduler.py
```

Open the dashboard:

```
streamlit run dashboard/dashboard.py
```

Check the results in SQL:

```sql
SELECT city, observed_at, us_aqi, aqi_category
FROM clean_aqi
ORDER BY observed_at DESC, city;
```

## Known limitations

- Every run reloads all CSV files into `raw_aqi`, so the raw table grows with copies. `clean_aqi` stays correct because it deduplicates, but the raw load is not idempotent yet.
- The scheduler is a Python loop. It only runs while the terminal is open and the computer is awake.
- Categories use the US AQI scale, not the Indian CPCB scale.
- The API updates about once an hour, so extra runs in between add no new readings.

## Next steps

- Make the raw load idempotent (unique key + `ON CONFLICT DO NOTHING`)
- Compute the Indian CPCB category from PM2.5 and PM10
- Store raw files in AWS S3 and load into Snowflake
- Move the cleaning SQL into dbt with tests
- Replace `scheduler.py` with Airflow
- Add more cities
