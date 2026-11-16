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
    "timezone": "Africa/Dakar"
}


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
    def load(summary):
        """
        #### Load task
        Insert the daily summary into the database (upsert on date).
        """
        load_daily(summary)


    raw_data = extract()
    transformed_data = transform(raw_data)
    load(transformed_data)



weather_etl()