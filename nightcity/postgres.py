import psycopg2
from psycopg2.extensions import connection

from nightcity.settings import identity, settings


def pg_connection(database_name: str = "postgres") -> connection:
    """Establish a connection to Postgres using Token Authentication."""
    return psycopg2.connect(
        user="nightcity",
        password=identity.get_token("https://ossrdbms-aad.database.windows.net/.default").token,
        host=settings.postgres_host,
        port=5432,
        dbname=database_name,
        sslmode="require",
    )
