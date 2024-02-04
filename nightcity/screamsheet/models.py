from sqlalchemy import Table
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.schema import MetaData

from nightcity.postgres import sqla_connection

engine: Engine = sqla_connection(database_name="polaris")
metadata: MetaData = MetaData()


class Base(DeclarativeBase):
    """Base model for SQLAlchemy."""


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
