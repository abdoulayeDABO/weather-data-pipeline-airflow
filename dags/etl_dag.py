from datetime import datetime

from airflow.sdk import DAG, task
from airflow.providers.standard.operators.bash import BashOperator

import json
import urllib.error
import urllib.parse
import urllib.request


def build_url(url, params):
    return f"{url}?{urllib.parse.urlencode(params)}"


def get_weather(url, params, timeout=10):
    full_url = build_url(url, params)
    # print(full_url)
    try:
        with urllib.request.urlopen(full_url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"Erreur réseau : {e}")
    except json.JSONDecodeError as e:
        print(f"Réponse JSON invalide : {e}")
    return None


with DAG(dag_id="wheather_etl"):
 
    @task
    def extract():
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 14.6937,
            "longitude": -17.4441,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
            "timezone": "Africa/Dakar",
        }
        weather = get_weather(url, params)
        print(weather)

  
    extract()