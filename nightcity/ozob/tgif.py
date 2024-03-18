"""SFTP implementation for TGI Fridays."""

import json
from io import StringIO

import paramiko

from nightcity.azure import blob_client, keyvault_client
from nightcity.settings import log


def run() -> None:
    """SFTP to Blob Storage function for TGI Fridays."""
    tgif_secret = json.loads(keyvault_client.get_secret("tgi-fridays-sftp").value)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key = paramiko.RSAKey.from_private_key(StringIO(tgif_secret["key"]))
    ssh_client.connect(
        hostname=tgif_secret["host"],
        port=tgif_secret["port"],
        username=tgif_secret["user"],
        password=tgif_secret["pass"],
        pkey=private_key,
        disabled_algorithms={"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]},
    )
    sftp = ssh_client.open_sftp()
    files_to_move = sftp.listdir("/Bink")
    for file in files_to_move:
        if not file.endswith(".csv"):
            log.info(f"Skipping {file} as it is not a CSV file.")
            continue
        log.info(f"Uploading {file} to blob storage.")
        with sftp.open(f"/Bink/{file}", "rb") as f:
            file_data = f.read()
        blob_client.get_blob_client(
            container="harmonia-imports",
            blob=f"scheme/tgi-fridays/{file}",
        ).upload_blob(file_data)
        log.info(f"Moving {file} to /Archive.")
        sftp.rename(f"/Bink/{file}", f"/Archive/{file}")
