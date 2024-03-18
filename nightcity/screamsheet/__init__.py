import typer

app = typer.Typer()


@app.command(name="transactions")
def transactions() -> None:
    """Send Transactions to Viator."""
    from .main import send_transcation_info

    send_transcation_info()


@app.command(name="marketing")
def marketing() -> None:
    """Send Marketing Preference to Viator."""
    from .main import send_marketing_info

    send_marketing_info()
