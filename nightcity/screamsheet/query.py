"""Query the Polaris and Harmonia databases for marketing preferences and transaction data."""

import pendulum
from sqlalchemy import String, select
from sqlalchemy.engine.row import Row
from sqlalchemy.sql import expression, func

from nightcity.settings import log, settings

if settings.postgres_host and settings.environment in ("prod", "staging"):
    from nightcity.screamsheet.models import (
        AccountHolder,
        AccountHolderMarketingPreference,
        AccountHolderProfile,
        ExportTransaction,
        RetailerConfig,
        engine,
    )


def get_marketing_data() -> list[Row]:
    """Get marketing preferences from the Polaris database."""
    conn = engine("polaris").connect()
    data = conn.execute(
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
    log.info(f"Retrieved {len(data)} rows from the database")
    log.debug(data)
    return data


def get_transaction_data() -> list[Row]:
    """Get transaction data from the Harmonia Database."""
    conn = engine("harmonia").connect()
    data = conn.execute(
        select(
            expression.cast(func.round(ExportTransaction.spend_amount / 100, 2), String),
            func.date_trunc("minute", ExportTransaction.transaction_date),
            ExportTransaction.auth_code,
            ExportTransaction.mid,
            ExportTransaction.last_four,
        )
        .where(ExportTransaction.transaction_date > pendulum.today().subtract(days=7))
        .where(ExportTransaction.provider_slug == "bpl-viator")
    ).fetchall()
    log.info(f"Retrieved {len(data)} rows from the database")
    log.debug(data)
    return data
