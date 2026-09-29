from scripts.config import DB_NAME
from scripts.load_aqi import connect


def clean():
    conn = connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM raw_aqi")
    raw_count = cur.fetchone()[0]

    cur.execute("DROP TABLE IF EXISTS clean_aqi")
    cur.execute("""
        CREATE TABLE clean_aqi AS
        SELECT
            city, observed_at, us_aqi, pm2_5, pm10, carbon_monoxide,
            nitrogen_dioxide, sulphur_dioxide, ozone, fetched_at,
            CASE
                WHEN us_aqi <= 50  THEN 'Good'
                WHEN us_aqi <= 100 THEN 'Moderate'
                WHEN us_aqi <= 150 THEN 'Unhealthy for Sensitive Groups'
                WHEN us_aqi <= 200 THEN 'Unhealthy'
                WHEN us_aqi <= 300 THEN 'Very Unhealthy'
                ELSE 'Hazardous'
            END AS aqi_category
        FROM (
            SELECT DISTINCT ON (city, observed_at) *
            FROM raw_aqi
            WHERE us_aqi IS NOT NULL
            ORDER BY city, observed_at, fetched_at DESC
        ) AS deduped
    """)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM clean_aqi")
    clean_count = cur.fetchone()[0]

    print(f"raw_aqi rows:   {raw_count}")
    print(f"clean_aqi rows: {clean_count}")
    print(f"Rows removed:   {raw_count - clean_count}")

    cur.execute("""
        SELECT city, observed_at, us_aqi, aqi_category
        FROM clean_aqi
        ORDER BY observed_at DESC, city
    """)
    print()
    for row in cur.fetchall():
        print(row)

    cur.close()
    conn.close()


if __name__ == "__main__":
    clean()