"""Main module for Night City."""
import typer
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated

from nightcity import delamain


class Config(BaseSettings):
    """Config for Night City."""

    model_config = SettingsConfigDict(env_prefix="NIGHTCITY_")


config = Config()
cli = typer.Typer()


@cli.command(name="delamain")
def cli_delamain(lookups: Annotated[str, typer.Option(help="A comma seperated list of hostnames to lookup.")]) -> None:
    """Delamain 'taxis' DNS records to NextDNS from Azure DNS / Kubernetes.

    Example: delamain --lookups=uksouth-dev-n71o.postgres.database.azure.com,uksouth-dev-05da.redis.cache.windows.net
    """
    delamain.run(lookups=lookups)


if __name__ == "__main__":
    cli()
