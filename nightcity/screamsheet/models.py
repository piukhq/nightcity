from sqlalchemy import Table
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.schema import MetaData

from nightcity.postgres import sqla_connection

metadata: MetaData = MetaData()


def engine(database_name: str) -> Engine:
    """Get the engine."""
    return sqla_connection(database_name=database_name)


class Base(DeclarativeBase):
    """Base model for SQLAlchemy."""


class AccountHolder(Base):
    """Account holder model."""

    __table__ = Table("account_holder", metadata, autoload_with=engine("polaris"))


class AccountHolderMarketingPreference(Base):
    """Account holder marketing preference model."""

    __table__ = Table("account_holder_marketing_preference", metadata, autoload_with=engine("polaris"))


class AccountHolderProfile(Base):
    """Account holder profile model."""

    __table__ = Table("account_holder_profile", metadata, autoload_with=engine("polaris"))


class RetailerConfig(Base):
    """Retailer config model."""

    __table__ = Table("retailer_config", metadata, autoload_with=engine("polaris"))


class ExportTransaction(Base):
    """Export Transaction model."""

    __table__ = Table("export_transaction", metadata, autoload_with=engine("harmonia"))
