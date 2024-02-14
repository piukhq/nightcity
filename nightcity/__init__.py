"""Main module for Night City."""
import typer
from typing_extensions import Annotated

from nightcity.brendan import run as brendan
from nightcity.delamain import run as delamain
from nightcity.ncpd import run as ncpd
from nightcity.screamsheet import run as screamsheet

cli = typer.Typer()


@cli.command(name="brendan")
def cli_brendan() -> None:
    """Add/Remove users from Postgres based on Entra ID Group Membership."""
    brendan()


@cli.command(name="delamain")
def cli_delamain() -> None:
    """Configure NextDNS Rewrites based on DNS Lookups from within Kubernetes."""
    delamain()


@cli.command(name="screamsheet")
def cli_screamsheet() -> None:
    """Send Viator Marketing Preference emails."""
    screamsheet()


@cli.command(name="ncpd")
def cli_ncpd(all: Annotated[bool, typer.Argument()]) -> None:
    """Run NightCity Police Department."""
    ncpd()


if __name__ == "__main__":
    cli()
