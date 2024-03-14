"""Main module for Night City."""

import typer

cli = typer.Typer()
screamsheet = typer.Typer()
cli.add_typer(screamsheet, name="screamsheet")


@cli.command(name="brendan")
def cli_brendan() -> None:
    """Add/Remove users from Postgres based on Entra ID Group Membership."""
    from nightcity.brendan import run as brendan

    brendan()


@cli.command(name="delamain")
def cli_delamain() -> None:
    """Configure NextDNS Rewrites based on DNS Lookups from within Kubernetes."""
    from nightcity.delamain import run as delamain

    delamain()


@screamsheet.command(name="marketing")
def marketing() -> None:
    """Send Marketing Preference to Viator."""
    from nightcity.screamsheet import send_marketing_info

    send_marketing_info()


@screamsheet.command(name="transactions")
def transactions() -> None:
    """Send Transactions to Viator."""
    from nightcity.screamsheet import send_transcation_info

    send_transcation_info()


if __name__ == "__main__":
    cli()
