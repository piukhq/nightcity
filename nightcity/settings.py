import sys

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from loguru import logger as log
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Config for Night City."""

    keyvault_url: AnyHttpUrl

    log_level: str = "INFO"


settings = Settings()

log.remove()
log.add(sys.stdout, level=settings.log_level)

identity = DefaultAzureCredential()
keyvault_client = SecretClient(vault_url=settings.keyvault_url, credential=identity)
