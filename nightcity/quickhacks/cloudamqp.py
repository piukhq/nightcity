"""Simple HTTP Proxy for CloudAMQP Prometheus Metrics."""

from typing import Annotated

import requests
from fastapi import FastAPI, Query, Request
from fastapi.responses import Response
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for CloudAMQP Proxy."""

    hostname: str
    username: str
    password: str

    model_config = SettingsConfigDict(env_prefix="CLOUDAMQP_")


app = FastAPI()
settings = Settings()


@app.get("/livez")
def livez() -> Response:
    """Liveness Check Endpoint."""
    return Response(content="OK", media_type="text/plain", status_code=200)


@app.get("/readyz")
def readyz() -> Response:
    """Readiness Check Endpoint."""
    response = requests.get(
        f"https://{settings.hostname}/metrics", auth=(settings.username, settings.password), timeout=5
    )
    response.raise_for_status()
    return Response(content="OK", media_type="text/plain", status_code=200)


@app.get("/metrics")
@app.get("/metrics/detailed")
def metrics(request: Request, family: Annotated[list[str] | None, Query()] = None) -> Response:
    """Fetch CloudAMQP Prometheus Metrics and return them."""
    response = requests.get(
        f"https://{settings.hostname}/{request.url.path}",
        params={"family": family} if family else None,
        auth=(settings.username, settings.password),
        timeout=5,
    )
    return Response(content=response.text, media_type="text/plain", status_code=response.status_code)
