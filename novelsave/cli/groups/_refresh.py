import click

from .. import controllers
from ..main import cli


@cli.command(name='refresh')
@click.argument('id_or_url')
def _refresh(
        id_or_url: str,
):
    """run update and compile consecutively"""
    controllers.update(id_or_url)
    controllers.compile(id_or_url)
