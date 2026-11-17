from datetime import datetime
from pydantic import BaseModel, ConfigDict

class WeatherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country: str
    temp: float
    temp_min: float | None
    temp_max: float | None
    feels_like: float
    main: str
    description: str
    rain_1h: float | None
    wind_speed: float | None
    collected_at: datetime
