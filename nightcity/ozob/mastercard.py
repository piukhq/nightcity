"""SFTP Implementation for Mastercard."""

import json
from io import BytesIO, StringIO, TextIOWrapper

import paramiko

from nightcity.azure import blob_client, keyvault_client
from nightcity.prometheus import sftp_connect
from nightcity.settings import log


def run(testing: bool = False) -> None:  # noqa: FBT001, FBT002
    """SFTP to Blob Storage function for Mastercard."""
    mastercard_secret = json.loads(keyvault_client.get_secret("mastercard-sftp").value)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key = paramiko.RSAKey.from_private_key(StringIO(mastercard_secret["key"]))
    sftp_file_path = "/0073185/production/download/TGX2" if not testing else "/0073185/test/download/TGX4"
    ssh_client.connect(
        hostname="files.mastercard.com" if not testing else "mtf.files.mastercard.com",
        port=16022,
        username="Z216458" if not testing else "Z218502",
        pkey=private_key,
        disabled_algorithms={"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]},
    )
    sftp = ssh_client.open_sftp()
    try:
        sftp.listdir()
    except OSError as e:
        sftp_connect.labels(
            status="failure",
            reason=e,
        ).set(1)
    else:
        sftp_connect.labels(
            status="success",
            reason="",
        ).set(0)
    for filename in sftp.listdir(sftp_file_path):
        log.info(f"Processing {filename}.")
        settlement_client = blob_client.get_blob_client(
            container="harmonia-imports",
            blob=f"mastercard-settlement/{filename}",
        )
        refund_client = blob_client.get_blob_client(
            container="harmonia-imports",
            blob=f"mastercard-refund/{filename}",
        )
        fo = BytesIO()
        sftp.getfo(f"{sftp_file_path}/{filename}", fo)
        fo.seek(0)
        content = TextIOWrapper(fo, encoding="utf-8")
        settlement_file = StringIO()
        refund_file = StringIO()
        for line in content:
            if line[0] != "D":
                # non-data records get written to both files
                settlement_file.write(line)
                refund_file.write(line)
            else:
                # data records get written to the appropriate file based on the spend amount
                spend_amount = int(line[slice(518, 518 + 12)])
                file = settlement_file if spend_amount >= 0 else refund_file
                file.write(line)
        settlement_file.seek(0)
        settlement_client.upload_blob(settlement_file.read())
        refund_file.seek(0)
        refund_client.upload_blob(refund_file.read())
