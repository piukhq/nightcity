"""Manages Azure Privledged Identity Management."""

import typer

app = typer.Typer()


@app.command()
def postgres() -> None:
    """Sync Group Memberships with Postgres."""
    from .postgres import run

    run()
