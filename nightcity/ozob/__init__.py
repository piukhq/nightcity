"""SFTP Implementations."""

import typer
from typing_extensions import Annotated

app = typer.Typer()


@app.command()
def tgif() -> None:
    """SFTP to Blob Storage service for TGI Fridays."""
    from nightcity.ozob.tgif import run

    run()


@app.command()
def mastercard(testing: Annotated[bool, typer.Option(help="Connect to the non-production SFTP Site")] = False) -> None:  # noqa: FBT002
    """SFTP to Blob Storage service for Mastercard."""
    from nightcity.ozob.mastercard import run

    run(testing=testing)
