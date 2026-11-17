import requests

from fastapi import APIRouter, HTTPException, Query

from weather.models import WeatherRecord
from weather.schemas import WeatherResponse
from weather.services import import_weather

router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("", response_model=list[WeatherResponse])
def get_weather(city: str | None = None):
    records = WeatherRecord.objects.all().order_by("-collected_at")

    if city:
        records = records.filter(name__iexact=city)

    return list(records)

@router.post(
    "/import",
    response_model=WeatherResponse,
    status_code=201
)
def create_weather(
    lat: float = Query(ge=-90, le=90),
    lon: float = Query(ge=-180, le=180)
):
    try:
        return import_weather(lat, lon)

    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Erro ao consultar a OpenWeather."
        )

    except ValueError:
        raise HTTPException(
            status_code=500,
            detail="Configuração da OpenWeather inválida."
        )

    except (KeyError, IndexError, TypeError):
        raise HTTPException(
            status_code=502,
            detail="Resposta inesperada da OpenWeather."
        )