"""Functions for interacting with Azure services."""

import asyncio

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
from msgraph import GraphServiceClient

from nightcity.settings import settings

identity = DefaultAzureCredential()

keyvault_client = SecretClient(vault_url=str(settings.keyvault_url), credential=identity)

blob_client: BlobServiceClient = BlobServiceClient(
    account_url=f"https://{settings.blob_storage_account_name}.blob.core.windows.net", credential=identity
)

sftp_client: BlobServiceClient = BlobServiceClient(
    account_url=f"https://{settings.sftp_storage_account_name}.blob.core.windows.net", credential=identity
)


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
