"""Manages the users in Postgres based on Entra ID Group Membership."""

import asyncio

from msgraph import GraphServiceClient

from nightcity.postgres import pg_connection
from nightcity.settings import identity, log, settings


class MicrosoftGraph:
    """Manages Microsoft Graph."""

    def __init__(self) -> None:
        """Initialise the Microsoft Graph Class."""
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.client = GraphServiceClient(credentials=identity, scopes=self.scopes)

    def get_group_members_by_email(self, group_id: str) -> list[str]:
        """Get email addresses of all members of a group from Microsoft Graph."""
        return [
            user.mail
            for user in asyncio.get_event_loop()
            .run_until_complete(self.client.groups.by_group_id(group_id).members.get())
            .value
        ]


class PGUserManager:
    """Manages Postgres Users."""

    def __init__(self) -> None:
        """Initialise the Postgres User Manager."""
        self.connection = pg_connection()

    def get_current_users(self) -> dict:
        """Get a list of current entra users from Postgres."""
        with self.connection as conn, conn.cursor() as cur:
            cur.execute("SELECT rolname FROM pgaadauth_list_principals(false);")
            all_users = [user[0] for user in cur.fetchall()]

            cur.execute("SELECT rolname FROM pgaadauth_list_principals(true);")
            admins = [user[0] for user in cur.fetchall()]
            readers = [user for user in all_users if user not in admins]
            admins.pop(admins.index("nightcity"))
            return {"admins": admins, "readers": readers}

    def remove_user(self, user: str) -> None:
        """Remove an entra user from Postgres."""
        log.info(f"Removing User: {user}")
        with self.connection as conn, conn.cursor() as cur:
            cur.execute(f'DROP ROLE "{user}";')

    def add_user(self, user: str, is_admin: bool) -> None:  # noqa: FBT001
        """Add an entra user to Postgres."""
        log.info(f"Adding User: {user}")
        with self.connection as conn, conn.cursor() as cur:
            if is_admin:
                cur.execute(f"SELECT * FROM pgaadauth_create_principal('{user}', true, true);")
                cur.execute(f'GRANT pg_read_all_data TO "{user}";')
                cur.execute(f'GRANT pg_write_all_data TO "{user}";')
            else:
                cur.execute(f"SELECT * FROM pgaadauth_create_principal('{user}', false, true);")
                cur.execute(f'GRANT pg_read_all_data TO "{user}";')


def run() -> None:
    """Add and remove users from postgres."""
    graph = MicrosoftGraph()
    pg = PGUserManager()

    entra_admins = graph.get_group_members_by_email(settings.entra_postgres_admins_group_id)
    entra_readers = graph.get_group_members_by_email(settings.entra_postgres_readers_group_id)

    pg_users = pg.get_current_users()

    duplicates = [user for user in entra_admins if user in entra_readers]
    for duplicate in duplicates:
        log.warning(f"User: {duplicate} found in both admins and readers. Removing from admins.")
        entra_admins.pop(entra_admins.index(duplicate))

    admins_to_add = [user for user in entra_admins if user not in pg_users["admins"]]
    readers_to_add = [user for user in entra_readers if user not in pg_users["readers"]]
    admins_to_remove = [user for user in pg_users["admins"] if user not in entra_admins]
    readers_to_remove = [user for user in pg_users["readers"] if user not in entra_readers]

    for user in admins_to_remove:
        pg.remove_user(user)

    for user in readers_to_remove:
        pg.remove_user(user)

    for user in admins_to_add:
        pg.add_user(user, is_admin=True)

    for user in readers_to_add:
        pg.add_user(user, is_admin=False)
