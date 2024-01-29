from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from sqlalchemy import Table, create_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base
from sqlalchemy.sql.schema import MetaData


class ScreamsheetConfig(BaseSettings):
    """Config for Screamsheet."""

    secrets_path: str = "/mnt/secrets"
    postgres_dsn: PostgresDsn = "postgresql://postgres:postgres@postgres:5432/polaris"

    blob_storage_connection_string: str = ""
    blob_container: str = "viator"

    mailgun_from: str = "noreply@bink.com"
    mailgun_to: str = "onlineservices@bink.com"


settings = ScreamsheetConfig()

engine = create_engine(str(settings.postgres_dsn))
metadata = MetaData()
Base: DeclarativeMeta = declarative_base(metadata=metadata)


class AccountHolder(Base):
    """Account holder model."""

    __table__ = Table("account_holder", metadata, autoload_with=engine)


class AccountHolderMarketingPreference(Base):
    """Account holder marketing preference model."""

    __table__ = Table("account_holder_marketing_preference", metadata, autoload_with=engine)


class AccountHolderProfile(Base):
    """Account holder profile model."""

    __table__ = Table("account_holder_profile", metadata, autoload_with=engine)


class RetailerConfig(Base):
    """Retailer config model."""

    __table__ = Table("retailer_config", metadata, autoload_with=engine)
