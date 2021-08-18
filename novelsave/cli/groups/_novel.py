import click

from .. import controllers
from ..main import cli


@cli.command(name='compile')
@click.argument('id_or_url')
def _compile(id_or_url: str):
    """compile the specified novel to epub"""
    controllers.compile(id_or_url)


@cli.command(name='refresh')
@click.argument('id_or_url')
@click.option('--limit', type=int, help='Maximum count of chapters to update. Set to 0 or less to skip.')
@click.option('--browser', help='Extract cookies from the specified browser and use them in subsequent requests.')
def _refresh(id_or_url: str, limit: int, browser: str):
    """runs 'update' and 'compile' commands consecutively"""
    controllers.update(id_or_url, browser, limit)
    controllers.compile(id_or_url)


@cli.command(name='update')
@click.argument('id_or_url')
@click.option('--limit', type=int, help='Maximum count of chapters to update. Set to 0 or less to skip.')
@click.option('--browser', help='Extract cookies from the specified browser and use them in subsequent requests.')
def _update(id_or_url: str, limit: int, browser: str):
    """Download the corresponding website of the novel and update the database"""
    controllers.update(id_or_url, browser, limit)


@cli.group(name='url')
def _url():
    """Handles novel url operations, add or delete"""


@_url.command(name='add')
@click.argument('id_or_url')
@click.argument('new_url')
def _add_url(id_or_url: str, new_url: str):
    """Add a url from a select novel"""
    controllers.add_url(id_or_url, new_url)


@_url.command(name='remove')
@click.argument('url')
def _remove_url(url: str):
    """Remove a url from a select novel"""
    controllers.remove_url(url)
