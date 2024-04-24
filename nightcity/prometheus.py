from prometheus_client import Gauge, push_to_gateway  # noqa: D100
from prometheus_client.registry import REGISTRY

from nightcity import settings
from nightcity.settings import log

sftp_connect = Gauge(
    name="sftp_connection_status",
    documentation="SFTP Connection Status",
    labelnames=("status", "reason"),
    registry=REGISTRY,
)


def push_metrics() -> None:
    """Push metrics to Prometheus."""
    try:
        push_to_gateway(
            settings.prometheus_push_gateway,
            job="nightcity",
            registry=REGISTRY,
        )
    except Exception as e:
        log.error("Error while pushing metrics to gateway: {}", e)
