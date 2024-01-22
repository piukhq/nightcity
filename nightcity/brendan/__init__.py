"""This code doesn't work yet, but it's a start."""  # noqa: D404

import psycopg
from loguru import logger
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class BrendanConfig(BaseSettings):
    """Config for Brendan."""

    database_url: PostgresDsn
    model_config = SettingsConfigDict(env_prefix="BRENDAN_")


settings = BrendanConfig()


def _get_current_users() -> list:
    with psycopg.connect(str(settings.database_url)) as conn, conn.cursor() as cur:
        cur.execute("SELECT rolname FROM pgaadauth_list_principals(false);")
        users = [user[0] for user in cur.fetchall()]
        logger.info(f"Found users: {users}")
        return users


def _remove_user(user: str) -> None:
    logger.info(f"Removing User: {user}")
    with psycopg.connect(str(settings.database_url)) as conn, conn.cursor() as cur:
        cur.execute(f'DROP ROLE "{user}";')


def _add_user(user: str) -> None:
    logger.info(f"Adding User: {user}")
    with psycopg.connect(str(settings.database_url)) as conn, conn.cursor() as cur:
        cur.execute(f"SELECT * FROM pgaadauth_create_principal('{user}', false, false);")
        cur.execute(f'GRANT pg_read_all_data TO "{user}";')


def run() -> None:
    """Add and remove users from postgres."""
    postgres_users = _get_current_users()
    entra_id_users = ["cpressland@bink.com", "nread@bink.com", "njames@bink.com", "tviknarajah@bink.com"]

    users_to_add = [user for user in entra_id_users if user not in postgres_users]
    for user in users_to_add:
        _add_user(user)

    users_to_remove = [user for user in postgres_users if user not in entra_id_users]
    for user in users_to_remove:
        _remove_user(user)
