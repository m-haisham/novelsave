import click

from .. import controllers
from ..main import cli


@cli.command(name='refresh')
@click.argument('id_or_url')
@click.option('--limit', type=int, help='Maximum count of chapters to update. Set to 0 or less to skip.')
@click.option('--browser', help='Extract cookies from the specified browser and use them in subsequent requests.')
def _refresh(id_or_url: str, limit: int, browser: str):
    """runs 'update' and 'compile' commands consecutively"""
    controllers.update(id_or_url, browser, limit)
    controllers.compile(id_or_url)
