import csv
import json
from io import StringIO

import pendulum
import requests
from box import Box
from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests.auth import HTTPBasicAuth
from sqlalchemy import select
from sqlalchemy.engine.row import Row
from sqlalchemy.sql import func
from tenacity import retry, stop_after_attempt, wait_fixed

from nightcity.settings import keyvault_client, log, settings
from nightcity.storage import sftp_client

if settings.postgres_host:
    from nightcity.screamsheet.models import (
        AccountHolder,
        AccountHolderMarketingPreference,
        AccountHolderProfile,
        RetailerConfig,
        engine,
    )


class ScreamsheetConfig(BaseSettings):
    """Config for Screamsheet."""

    mailgun_from: EmailStr = "noreply@bink.com"
    mailgun_to: EmailStr = "onlineservices@bink.com"

    model_config = SettingsConfigDict(env_prefix="SCREAMSHEET_")


app_settings = ScreamsheetConfig()


def get_marketing_data() -> list[Row]:
    """Get marketing preferences from the Polaris database."""
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


def prepare_csv(data: list[Row]) -> StringIO:
    """Write Marketing Preferences to a CSV StringIO Object."""
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
    file_writer.writerows(data)
    return f


def generate_filename() -> str:
    """Generate a Filename for Azure Storage."""
    date = pendulum.now(tz="utc").strftime("%Y-%m-%d_%H-%M-%S")
    return f"downloads/Marketing_Preferences_{date}.csv"


def upload_blob(file: StringIO, filename: str) -> None:
    """Upload Data to Azure Storage."""
    blob = sftp_client.get_blob_client(
        container="viator",
        blob=filename,
    )
    blob.upload_blob(file.read())


@retry(stop=stop_after_attempt(3), wait=wait_fixed(10))
def send_email_via_mailgun() -> None:
    """Send an email via Mailgun."""
    message = """
    Hi Viator Team,

    Please note the monthly Viator Marketing preference file has been uploaded to the SFTP

    Thanks
    Bink Team
    """

    mailgun_secret = Box(json.loads(keyvault_client.get_secret("mailgun").value))

    if mailgun_secret.MAILGUN_API_KEY == "fake-api-key":
        log.error("Mailgun API Key is not set")
        return

    try:
        r = requests.post(
            f"{mailgun_secret.MAILGUN_API}/{mailgun_secret.MAILGUN_DOMAIN}/messages",
            auth=HTTPBasicAuth("api", mailgun_secret.MAILGUN_API_KEY),
            data={
                "from": str(app_settings.mailgun_from),
                "to": str(app_settings.mailgun_to),
                "subject": "Viator Marketing Preferences",
                "text": message,
            },
            timeout=10,
        )
        r.raise_for_status()
    except requests.RequestException:
        log.exception("Mailgun Request Failed")


def run() -> None:
    """Entrypoint for Screamsheet."""
    marketing_data = get_marketing_data()
    file = prepare_csv(marketing_data)
    file.seek(0)
    filename = generate_filename()
    upload_blob(file=file, filename=filename)
    send_email_via_mailgun()
