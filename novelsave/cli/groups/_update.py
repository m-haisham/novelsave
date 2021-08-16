import click

from .. import controllers
from ..main import cli


@cli.command(name='update')
@click.argument('id_or_url')
@click.option('--limit', type=int, help='Maximum count of chapters to update. Set to 0 or less to skip.')
@click.option('--browser', help='Extract cookies from the specified browser and use them in subsequent requests.')
def _update(id_or_url: str, limit: int, browser: str):
    """Download the corresponding website of the novel and update the database"""
    controllers.update(id_or_url, browser, limit)
