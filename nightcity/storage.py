from azure.storage.blob import BlobServiceClient

from nightcity.settings import identity, settings

blob_client: BlobServiceClient = BlobServiceClient(
    account_url=f"https://{settings.blob_storage_account_name}.blob.core.windows.net", credential=identity
)

sftp_client: BlobServiceClient = BlobServiceClient(
    account_url=f"https://{settings.sftp_storage_account_name}.blob.core.windows.net", credential=identity
)
