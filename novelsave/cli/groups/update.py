import click

from .. import controllers
from ..main import cli


@cli.command()
@click.argument('id_or_url')
@click.option('--limit', type=int, help='Maximum count of chapters to update. Set to 0 or less to skip.')
def update(
        id_or_url: str,
        skip_chapters: bool,
):
    """check and update a novel"""
    controllers.update(id_or_url, skip_chapters)
