"""Main module for Night City."""
import typer

from nightcity.brendan import run as brendan
from nightcity.delamain import run as delamain

cli = typer.Typer()


@cli.command(name="brendan")
def cli_brendan() -> None:
    """Add/Remove users from Postgres based on Entra ID Group Membership."""
    brendan()


@cli.command(name="delamain")
def cli_delamain() -> None:
    """Configure NextDNS Rewrites based on DNS Lookups from within Kubernetes."""
    delamain()


if __name__ == "__main__":
    cli()
