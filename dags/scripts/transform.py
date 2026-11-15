import json
import logging
import urllib.error
from datetime import datetime
from pprint import pprint

from .extract import get_weather


def clean(values):
    return [v for v in values if v is not None]

def format_date(iso):
    return datetime.fromisoformat(iso).strftime("%Y-%m-%d")

def process_data(raw_data):
    hourly = raw_data["hourly"]

    temps = clean(hourly["temperature_2m"])
    humidity = clean(hourly["relative_humidity_2m"])
    rain = clean(hourly["precipitation"])
    wind = clean(hourly["wind_speed_10m"])

    return {
        "location": "Dakar",
        "date": format_date(hourly["time"][0]),
        "avg_temperature": round(sum(temps) / len(temps), 1),
        "avg_humidity": round(sum(humidity) / len(humidity), 1),
        "total_precipitation": round(sum(rain), 1),
        "max_wind_speed": max(wind),
    }
    


if __name__ == "__main__":

    url = "https://api.open-meteo.com/v1/forecast"
    query_params = {
        "latitude": 14.6937,
        "longitude": -17.4441,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "timezone": "Africa/Dakar",
        "forecast_days": 1,
    }
    try:
        raw = get_weather(url, query_params)
        processed = process_data(raw)
        pprint(processed, width=100, sort_dicts=False)
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        logging.error("Network error : %s", e)
  