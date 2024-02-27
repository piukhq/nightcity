"""Main module for Night City."""

import typer

from nightcity.brendan import run as brendan
from nightcity.delamain import run as delamain
from nightcity.screamsheet import get_marketing_data, get_transaction_data

cli = typer.Typer()

screamsheet = typer.Typer()
cli.add_typer(screamsheet, name="screamsheet")


@cli.command(name="brendan")
def cli_brendan() -> None:
    """Add/Remove users from Postgres based on Entra ID Group Membership."""
    brendan()


@cli.command(name="delamain")
def cli_delamain() -> None:
    """Configure NextDNS Rewrites based on DNS Lookups from within Kubernetes."""
    delamain()


@screamsheet.command(name="marketing")
def marketing() -> None:
    """Send Marketing Preference to Viator."""
    get_marketing_data()


@screamsheet.command(name="transactions")
def transactions() -> None:
    """Send Transactions to Viator."""
    get_transaction_data()


if __name__ == "__main__":
    cli()
