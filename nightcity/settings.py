import sys

import sentry_sdk
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from loguru import logger as log
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Config for Night City."""

    environment: str = "local"

    keyvault_url: AnyHttpUrl | None = None
    postgres_host: str | None = None
    postgres_user: str = "nightcity"

    entra_postgres_admins_group_id: str = "c1167db2-e6b6-457f-8c7b-7a38b80b86a7"
    entra_postgres_readers_group_id: str = "a3f47ff2-0d9b-46d3-ac36-44af5933f0d4"

    blob_storage_account_name: str | None = None
    sftp_storage_account_name: str | None = None

    log_level: str = "INFO"


settings = Settings()

log.remove()
log.add(sys.stdout, level=settings.log_level)

identity = DefaultAzureCredential()
keyvault_client = SecretClient(vault_url=str(settings.keyvault_url), credential=identity)

sentry_sdk.init(
    dsn="https://01f20b69b17dfb7a44f8f0282f1970bb@o503751.ingest.sentry.io/4506688692617216",
    environment=settings.environment,
)
