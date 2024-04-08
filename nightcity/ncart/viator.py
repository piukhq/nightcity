"""Blob Storage Implementation for Viator."""

from io import BytesIO

from nightcity.azure import blob_client, sftp_client
from nightcity.settings import log


def run() -> None:
    """Copy Blobs from Viator SFTP to Carina."""
    source_container = sftp_client.get_container_client("viator")
    destination_container = blob_client.get_container_client("carina-imports")
    for blob in source_container.list_blobs():
        if blob.name.startswith("uploads/"):
            filename = blob.name.split("/")[-1]
            log.info(f"Moving {blob.name} to carina-imports.")
            source_blob = source_container.get_blob_client(blob.name)
            destination_blob = destination_container.get_blob_client(f"viator/{filename}")
            fo = BytesIO()
            source_blob.download_blob().readinto(fo)
            fo.seek(0)
            destination_blob.upload_blob(fo)
            source_blob.delete_blob()
            log.info(f"Moved {blob.name} to carina-imports.")
