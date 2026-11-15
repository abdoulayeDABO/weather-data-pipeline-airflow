import json
import logging
import urllib.error
import urllib.parse
import urllib.request


def build_url(url, query_params):
    return f"{url}?{urllib.parse.urlencode(query_params)}"


def get_weather(url, query_params, timeout=10):
    full_url = build_url(url, query_params)
    with urllib.request.urlopen(full_url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    url = "https://api.open-meteo.com/v1/forecast"
    query_params = {
        "latitude": 14.6937,
        "longitude": -17.4441,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
        "timezone": "Africa/Dakar",
    }
    try:
        print(get_weather(url, query_params))
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        logging.error("Network error: %s", e)
        raise