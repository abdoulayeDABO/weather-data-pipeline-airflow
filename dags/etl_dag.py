from datetime import datetime

from airflow.sdk import dag, task, get_current_context
from scripts.extract import get_weather
from scripts.transform import process_data
from scripts.load import load_daily

URL = "https://api.open-meteo.com/v1/forecast"
BASE_PARAMS = {
    "latitude": 14.6937,
    "longitude": -17.4441,
    "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
    "timezone": "Africa/Dakar",
}

REQUIRED_FIELDS = ["avg_temperature", "avg_humidity", "total_precipitation", "max_wind_speed"]


def check_quality(row: dict) -> None:
    """Raise ValueError listing every problem found in the daily summary."""
    errors = []

    for field in REQUIRED_FIELDS:
        if row.get(field) is None:
            errors.append(f"{field} is missing")

    temp = row.get("avg_temperature")
    if temp is not None and not (-10 <= temp <= 55):
        errors.append(f"avg_temperature out of range: {temp}")

    hum = row.get("avg_humidity")
    if hum is not None and not (0 <= hum <= 100):
        errors.append(f"avg_humidity out of range: {hum}")

    rain = row.get("total_precipitation")
    if rain is not None and rain < 0:
        errors.append(f"total_precipitation is negative: {rain}")

    wind = row.get("max_wind_speed")
    if wind is not None and not (0 <= wind <= 200):
        errors.append(f"max_wind_speed out of range: {wind}")

    if errors:
        raise ValueError("Data quality check failed: " + "; ".join(errors))


@dag(
    dag_id="weather_etl",
    description="Daily ETL pipeline for Dakar weather data (Open-Meteo API)",
    start_date=datetime(2026, 11, 8),
    schedule="@daily",
    catchup=True,
    default_args={"retries": 2},
    tags=["weather", "etl"],
)
def weather_etl():
    @task
    def extract():
        """
        #### Extract task
        Call the Open-Meteo API and return the raw JSON response
        (24 hourly values per variable for the current day).
        """
        context = get_current_context()
        day = context["logical_date"].strftime("%Y-%m-%d")
        params = {**BASE_PARAMS, "start_date": day, "end_date": day}
        return get_weather(URL, params)

    @task
    def transform(raw_data):
        """
        #### Transform task
        Aggregate the 24 hourly values into one daily summary:
        date, average temperature, average humidity,
        total precipitation and maximum wind speed.
        """
        return process_data(raw_data)

    @task
    def check(summary):
        """
        #### Data quality check task
        Validate the daily summary (no missing values, values in a
        plausible range). Fails the run before anything is loaded.
        """
        check_quality(summary)
        return summary

    @task
    def load(summary):
        """
        #### Load task
        Insert the daily summary into the database (upsert on date).
        """
        load_daily(summary)

    raw_data = extract()
    transformed_data = transform(raw_data)
    checked_data = check(transformed_data)
    load(checked_data)


weather_etl()