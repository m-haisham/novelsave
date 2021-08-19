import click

from .. import controllers
from ..main import cli


@cli.command(name='package')
@click.argument('id_or_url')
def _package(id_or_url: str):
    """package the specified novel to epub"""
    controllers.package(id_or_url)


@cli.command(name='process')
@click.argument('id_or_url')
@click.option('--limit', type=int, help='Maximum count of chapters to update. Set to 0 or less to skip.')
@click.option('--browser', help='Extract cookies from the specified browser and use them in subsequent requests.')
def _process(id_or_url: str, limit: int, browser: str):
    """runs 'update' and 'package' commands consecutively"""
    controllers.update(id_or_url, browser, limit)
    controllers.package(id_or_url)


@cli.command(name='update')
@click.argument('id_or_url')
@click.option('--limit', type=int, help='Maximum count of chapters to update. Set to 0 or less to skip.')
@click.option('--browser', help='Extract cookies from the specified browser and use them in subsequent requests.')
def _update(id_or_url: str, limit: int, browser: str):
    """Scrape the website of the novel and update the database"""
    controllers.update(id_or_url, browser, limit)


@cli.group(name='novel')
def _novel():
    """Group of commands to manage novels"""


@_novel.command(name='clean')
@click.argument('id_or_url')
@click.option('--content-only', is_flag=True, help="Only remove chapter content")
def _clean_novel(id_or_url: str, content_only: bool):
    """Removes all except vital information related to novel"""
    controllers.clean_novel(id_or_url, content_only)


@_novel.command(name='delete')
@click.argument('id_or_url')
def _delete_novel(id_or_url: str):
    """Remove novel entry from database"""
    controllers.delete_novel(id_or_url)


@_novel.group(name='url')
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
