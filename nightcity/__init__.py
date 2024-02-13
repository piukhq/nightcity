"""Main module for Night City."""
import typer

from nightcity.brendan import run as brendan
from nightcity.delamain import run as delamain
from nightcity.screamsheet import run as screamsheet
from nightcity.ncpd import assets

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


if __name__ == "__main__":
    cli()
