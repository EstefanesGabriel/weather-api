import os

from django.core.asgi import get_asgi_application
from fastapi import FastAPI

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django_app = get_asgi_application()

from weather.routes import router

app = FastAPI(
    title="Weather API",
    description="API para coleta e consulta de dados meteorológicos.",
    version="1.0.0"
)

app.include_router(router)

app.mount("/", django_app)