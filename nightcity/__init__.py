"""Main module for Night City."""
import typer

from nightcity.delamain import run as delamain

cli = typer.Typer()


@cli.command(name="delamain")
def cli_delamain() -> None:
    """Delamain sends DNS records to NextDNS from Kubernetes for use with Tailscale."""
    delamain()


if __name__ == "__main__":
    cli()
