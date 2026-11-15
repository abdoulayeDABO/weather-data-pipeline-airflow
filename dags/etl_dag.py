from datetime import datetime

from airflow.sdk import dag, task
from scripts.extract import get_weather
from scripts.transform import process_data

URL = "https://api.open-meteo.com/v1/forecast"
QUERY_PARAMS = {
    "latitude": 14.6937,
    "longitude": -17.4441,
    "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
    "timezone": "Africa/Dakar",
    "forecast_days": 1, 
}


@dag(
    dag_id="weather_etl",
    description="Daily ETL pipeline for Dakar weather data (Open-Meteo API)",
    start_date=datetime(2026, 11, 1),
    schedule="@daily", 
    catchup=False, 
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
        return get_weather(URL, QUERY_PARAMS)

    @task
    def transform(raw_data):
        """
        #### Transform task
        Aggregate the 24 hourly values into one daily summary:
        date, average temperature, average humidity,
        total precipitation and maximum wind speed.
        """
        return process_data(raw_data)


    raw_data = extract()
    transformed_data = transform(raw_data)



weather_etl()