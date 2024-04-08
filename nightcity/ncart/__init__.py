"""Blob Storage Implementations."""

import typer

app = typer.Typer()


@app.command()
def itsu() -> None:
    """Blob Move Tool for Itsu."""
    from nightcity.ncart.itsu import run

    run()


@app.command()
def viator() -> None:
    """Blob Move Tool for Viator."""
    from nightcity.ncart.viator import run

    run()
