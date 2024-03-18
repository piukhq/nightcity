"""SFTP Implementations."""

import typer

app = typer.Typer()


@app.command()
def tgif() -> None:
    """SFTP to Blob Storage service for TGI Fridays."""
    from nightcity.ozob.tgif import run

    run()
