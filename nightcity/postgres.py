import psycopg2
from psycopg2.extensions import connection
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine

from nightcity.settings import identity, settings


def pg_connection(database_name: str = "postgres") -> connection:
    """Establish a connection to Postgres using Token Authentication."""
    return psycopg2.connect(
        user=settings.postgres_user,
        password=identity.get_token("https://ossrdbms-aad.database.windows.net/.default").token,
        host=settings.postgres_host,
        port=5432,
        dbname=database_name,
        sslmode="require",
    )


def sqla_connection(database_name: str = "postgres") -> Engine:
    """Establish a connection to Postgres using Token Authentication."""
    return create_engine(
        f"postgresql+psycopg2://{settings.postgres_user}:{identity.get_token('https://ossrdbms-aad.database.windows.net/.default').token}@{settings.postgres_host}:5432/{database_name}?sslmode=require",
    )
