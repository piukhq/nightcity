import sys

from loguru import logger as log
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Config for Night City."""

    nextdns_api_key: str
    nextdns_id: str

    log_level: str = "INFO"


settings = Settings()

log.remove()
log.add(sys.stdout, level=settings.log_level)
