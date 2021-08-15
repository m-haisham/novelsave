import click

from .. import controllers
from ..main import cli


@cli.command(name='refresh')
@click.argument('id_or_url')
@click.option('--limit', type=int, help='Maximum count of chapters to update. Set to 0 or less to skip.')
def _refresh(
        id_or_url: str,
        limit: int,
):
    """run update and compile consecutively"""
    controllers.update(id_or_url, limit)
    controllers.compile(id_or_url)
