import click

from .. import controllers
from ..main import cli


@cli.command(name='update')
@click.argument('id_or_url')
@click.option('--limit', type=int, help='Maximum count of chapters to update. Set to 0 or less to skip.')
def _update(
        id_or_url: str,
        limit: int,
):
    """check and update a novel"""
    controllers.update(id_or_url, limit)
