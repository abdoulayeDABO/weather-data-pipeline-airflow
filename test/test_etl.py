from ags.scripts.extract import get_weather
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))

URL = "https://api.open-meteo.com/v1/forecast"
QUERY_PARAMS = {
    "latitude": 14.6937,
    "longitude": -17.4441,
    "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
    "timezone": "Africa/Dakar",
}


def test_get_weather():
    data = get_weather(URL, QUERY_PARAMS)
    assert len(data) != 0
    
