"""Main module for Night City."""

from sys import platform

import typer

from nightcity import brendan, ncart, ozob, quickhacks, screamsheet

if platform == "linux":
    typer.core.rich = None


cli = typer.Typer()
cli.add_typer(brendan.app, name="brendan", help="PIM Functions.")
cli.add_typer(ozob.app, name="ozob", help="SFTP Functions.")
cli.add_typer(ncart.app, name="ncart", help="Blob Storage Functions.")
cli.add_typer(screamsheet.app, name="screamsheet", help="Viator Functions.")
cli.add_typer(quickhacks.app, name="quickhacks", help="Hacky Functions.")


if __name__ == "__main__":
    cli()
