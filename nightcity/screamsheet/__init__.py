import csv
import datetime
import json
import logging
from io import StringIO
from pathlib import Path

import requests
from azure.storage.blob import BlobClient
from models import (
    AccountHolder,
    AccountHolderMarketingPreference,
    AccountHolderProfile,
    RetailerConfig,
    engine,
    settings,
)
from requests.auth import HTTPBasicAuth
from sqlalchemy import select
from sqlalchemy.sql import func
from tenacity import retry, stop_after_attempt, wait_fixed


def read_secrets(key: str) -> str:
    """Read secrets from the secrets file."""
    try:
        path = Path(settings.secrets_path) / key
        with path.open() as f:
            return json.loads(f.read())
    except FileNotFoundError:
        logging.exception(f"Secrets file not found: {path}")
        raise


def get_info() -> list:
    """Get the marketing preference from the database."""
    conn = engine.connect()
    return conn.execute(
        select(
            AccountHolder.email,
            AccountHolderProfile.first_name,
            AccountHolderProfile.last_name,
            AccountHolderProfile.date_of_birth,
            AccountHolderMarketingPreference.key_name,
            AccountHolderMarketingPreference.value,
            AccountHolder.account_number,
            func.date(AccountHolderMarketingPreference.updated_at),
        )
        .join(RetailerConfig, RetailerConfig.id == AccountHolder.retailer_id)
        .join(
            AccountHolderMarketingPreference,
            AccountHolderMarketingPreference.account_holder_id == AccountHolder.id,
        )
        .join(
            AccountHolderProfile,
            AccountHolderProfile.account_holder_id == AccountHolder.id,
        )
        .where(AccountHolder.email.notlike(r"%\@\%"))
        .where(AccountHolder.email.notlike("%bink.com"))
        .where(AccountHolder.email.notlike("%test%"))
        .where(RetailerConfig.slug == "viator"),
    ).fetchall()


def write_file_to_memory() -> StringIO:
    """Write the marketing preference to a file."""
    info = get_info()
    f = StringIO()
    file_writer = csv.writer(f)
    file_writer.writerow(
        [
            "Email",
            "First Name",
            "Last Name",
            "Date of Birth",
            "Key Name",
            "Value",
            "Account Number",
            "Updated At",
        ],
    )
    file_writer.writerows(info)

    return f


def filename() -> str:
    """Create a filename for the file to be uploaded to the blob storage."""
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    date = now.strftime("%Y-%m-%d_%H-%M-%S")

    return f"downloads/Marketing_Preferences_{date}.csv"


def upload_file_to_blob() -> None:
    """Upload the file to the blob storage."""
    f = write_file_to_memory()
    f.seek(0)
    fname = filename()
    blob = BlobClient.from_connection_string(
        conn_str=settings.blob_storage_connection_string,
        container_name=settings.blob_container,
        blob_name=fname,
    )
    blob.upload_blob(f.read())


@retry(stop=stop_after_attempt(3), wait=wait_fixed(10))
def mailgun() -> None:
    """Send an email to the Viator team."""
    message = """
    Hi Viator Team,

    Please note the monthly Viator Marketing preference file has been uploaded to the SFTP

    Thanks
    Bink Team
    """

    mailgun_api_key: str = read_secrets("mailgun")["MAILGUN_API_KEY"]
    mailgun_url: str = f'{read_secrets("mailgun")["MAILGUN_API"]}/{read_secrets("mailgun")["MAILGUN_DOMAIN"]}/messages'

    try:
        requests.post(
            mailgun_url,
            auth=HTTPBasicAuth("api", mailgun_api_key),
            data={
                "from": settings.mailgun_from,
                "to": settings.mailgun_to,
                "subject": "Viator Marketing Preferences",
                "text": message,
            },
            timeout=10,
        )
    except Exception:
        logging.exception("Mailgun Request Failed")


def run() -> None:
    """Run the script."""
    upload_file_to_blob()
    mailgun()
