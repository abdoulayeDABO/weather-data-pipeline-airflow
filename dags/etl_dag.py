from datetime import datetime

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from scripts.extract import get_weather

URL = "https://api.open-meteo.com/v1/forecast"
QUERY_PARAMS = {
    "latitude": 14.6937,
    "longitude": -17.4441,
    "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
    "timezone": "Africa/Dakar",
}

with DAG(
    dag_id="weather_etl",
    start_date=datetime(2026, 11, 1),
    schedule=None,
    catchup=False,
):
    extract = PythonOperator(
        task_id="extract_weather",
        python_callable=get_weather,
        op_kwargs={"url": URL, "query_params": QUERY_PARAMS},
    )