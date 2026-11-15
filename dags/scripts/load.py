import psycopg2
import os

user = os.environ["POSTGRES_USER"]
password = os.environ["POSTGRES_PASSWORD"]
host = os.environ["POSTGRES_HOST"]
port = os.environ["POSTGRES_PORT"]
db = os.environ["POSTGRES_DB"]

dsn = f"postgresql://{user}:{password}@{host}:{port}/{db}"

def load_daily(summary):
    query = """
        INSERT INTO weather_daily
            (location, date, avg_temperature, avg_humidity,
             total_precipitation, max_wind_speed)
        VALUES (%(location)s, %(date)s, %(avg_temperature)s, %(avg_humidity)s,
                %(total_precipitation)s, %(max_wind_speed)s)
        ON CONFLICT (location, date) DO UPDATE SET
            avg_temperature     = EXCLUDED.avg_temperature,
            avg_humidity        = EXCLUDED.avg_humidity,
            total_precipitation = EXCLUDED.total_precipitation,
            max_wind_speed      = EXCLUDED.max_wind_speed,
            ingested_at         = now();
    """

    conn = psycopg2.connect(dsn)
    try:
        with conn, conn.cursor() as cur:
            cur.execute(query, summary)
    finally:
        conn.close()