import csv

import psycopg2

from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, RAW_DIR

COLUMNS = [
    "city", "observed_at", "us_aqi", "pm2_5", "pm10", "carbon_monoxide",
    "nitrogen_dioxide", "sulphur_dioxide", "ozone", "fetched_at",
]


def connect(dbname):
    if not DB_PASSWORD:
        raise RuntimeError("DB_PASSWORD not found. Check your .env file.")
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER,
        password=DB_PASSWORD, dbname=dbname,
    )


def create_database_if_missing():
    conn = connect("postgres")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    if not cur.fetchone():
        cur.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Created database: {DB_NAME}")
    cur.close()
    conn.close()


def blank_to_none(value):
    return None if value == "" else value


def load_csv_files():
    conn = connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_aqi (
            city              TEXT,
            observed_at       TIMESTAMP,
            us_aqi            INTEGER,
            pm2_5             NUMERIC,
            pm10              NUMERIC,
            carbon_monoxide   NUMERIC,
            nitrogen_dioxide  NUMERIC,
            sulphur_dioxide   NUMERIC,
            ozone             NUMERIC,
            fetched_at        TIMESTAMP
        )
    """)

    insert_sql = f"""
        INSERT INTO raw_aqi ({", ".join(COLUMNS)})
        VALUES ({", ".join(["%s"] * len(COLUMNS))})
    """

    inserted = 0
    for path in sorted(RAW_DIR.glob("aqi_*.csv")):
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                values = [blank_to_none(row[col]) for col in COLUMNS]
                cur.execute(insert_sql, values)
                inserted += 1

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM raw_aqi")
    total = cur.fetchone()[0]
    print(f"Inserted this run: {inserted}")
    print(f"Total rows in raw_aqi: {total}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    create_database_if_missing()
    load_csv_files()