
from django.db import models


class WeatherRecord(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=2)

    temp = models.FloatField()
    temp_min = models.FloatField(null=True)
    temp_max = models.FloatField(null=True)
    feels_like = models.FloatField()

    main = models.CharField(max_length=50)
    description = models.CharField(max_length=255)

    rain_1h = models.FloatField(null=True)
    wind_speed = models.FloatField(null=True)

    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "weather_records"

    def __str__(self):
        return f"{self.name} ({self.country}) - {self.temp}°C"
