"""Console script for zeroae-goblet."""

import sys

import click


@click.command()
def goblet(args=None):
    """Console script for zeroae-goblet."""
    # fmt: off
    click.echo("Replace this message by putting your code into "
               "goblet.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    # fmt: on
    return 0


if __name__ == "__main__":
    sys.exit(goblet)  # pragma: no cover
