"""DevOps Quickhacks."""

import typer

app = typer.Typer()


@app.command()
def stonegate() -> None:
    """Send Stonegate SMB Files to Boreas API."""
    from nightcity.quickhacks.stonegate import run

    run()
