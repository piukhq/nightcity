"""Simple HTTP Proxy for CloudAMQP Prometheus Metrics."""

from pathlib import Path
from typing import Annotated

import requests
from fastapi import FastAPI, Query, Request
from fastapi.responses import Response

from nightcity.azure import keyvault_client

username = keyvault_client.get_secret("infra-cloudamqp-username").value
password = keyvault_client.get_secret("infra-cloudamqp-password").value
statefulset_replica = int(Path("/etc/hostname").read_text().strip().split("-")[-1])
hostname = keyvault_client.get_secret(f"infra-cloudamqp-node-0{statefulset_replica + 1}").value

app = FastAPI()


@app.get("/livez")
def livez() -> Response:
    """Liveness Check Endpoint."""
    return Response(content="OK", media_type="text/plain", status_code=200)


@app.get("/readyz")
def readyz() -> Response:
    """Readiness Check Endpoint."""
    response = requests.get(f"https://{hostname}/metrics", auth=(username, password), timeout=5)
    response.raise_for_status()
    return Response(content="OK", media_type="text/plain", status_code=200)


@app.get("/metrics")
@app.get("/metrics/detailed")
def metrics(request: Request, family: Annotated[list[str] | None, Query()] = None) -> Response:
    """Fetch CloudAMQP Prometheus Metrics and return them."""
    response = requests.get(
        f"https://{hostname}/{request.url.path}",
        params={"family": family} if family else None,
        auth=(username, password),
        timeout=5,
    )
    return Response(content=response.text, media_type="text/plain", status_code=response.status_code)
