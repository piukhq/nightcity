"""Main module for Night City."""

import typer

from nightcity import brendan, ozob, screamsheet

cli = typer.Typer()
cli.add_typer(brendan.app, name="brendan", help="PIM Functions.")
cli.add_typer(ozob.app, name="ozob", help="SFTP Functions.")
cli.add_typer(screamsheet.app, name="screamsheet", help="Viator Functions.")


if __name__ == "__main__":
    cli()
