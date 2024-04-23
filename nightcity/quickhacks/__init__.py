"""DevOps Quickhacks."""

import typer

app = typer.Typer()


@app.command()
def stonegate() -> None:
    """Send Stonegate SMB Files to Boreas API."""
    from nightcity.quickhacks.stonegate import run

    run()


@app.command()
def cloudamqp() -> None:
    """Proxy CloudAMQP Prometheus Metrics."""
    import uvicorn

    uvicorn.run("nightcity.quickhacks.cloudamqp:app", host="127.0.0.1", port=6502)
