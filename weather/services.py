
import os
import requests

from weather.models import WeatherRecord


def import_weather(lat: float, lon: float) -> WeatherRecord:
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        raise ValueError("OpenWeather API Key não configurada.")

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
        "lang": "pt_br",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    weather = data["weather"][0]
    main = data["main"]

    record = WeatherRecord.objects.create(
        name=data["name"],
        country=data["sys"]["country"],
        temp=main["temp"],
        temp_min=main.get("temp_min"),
        temp_max=main.get("temp_max"),
        feels_like=main["feels_like"],
        main=weather["main"],
        description=weather["description"],
        rain_1h=data.get("rain", {}).get("1h"),
        wind_speed=data.get("wind", {}).get("speed"),
    )

    return record
