from typing import Iterable

import click

from .. import controllers
from ..main import cli


@cli.command(name='package')
@click.argument('id_or_url')
@click.option('--target', multiple=True, default=('epub', ),
              help="Target formats to package the novel ('epub', 'html', 'mobi', 'pdf', 'azw3').")
@click.option('--target-all', is_flag=True, help="Target all supported formats (overrides --target).")
def _package(id_or_url: str, target: Iterable[str], target_all: bool):
    """Package the specified novel to epub"""
    controllers.package(id_or_url, target, target_all)


@cli.command(name='process')
@click.argument('id_or_url')
@click.option('--limit', type=int, help='Maximum count of chapters to update. Set to 0 or less to skip.')
@click.option('--browser', help='Extract cookies from the specified browser and use them in subsequent requests.')
@click.option('--threads', type=int, help="Amount of threads to use when downloading chapters.")
@click.option('--target', multiple=True, default=('epub', ),
              help="Target formats to package the novel ('epub', 'html', 'mobi', 'pdf', 'azw3').")
@click.option('--target-all', is_flag=True, help="Target all supported formats (overrides --target).")
def _process(id_or_url: str, limit: int, browser: str, threads: int, target: Iterable[str]):
    """Runs 'update' and 'package' commands consecutively"""
    controllers.update(id_or_url, browser, limit, threads)
    controllers.package(id_or_url, target)


@cli.command(name='update')
@click.argument('id_or_url')
@click.option('--limit', type=int, help='Maximum count of chapters to update. Set to 0 or less to skip.')
@click.option('--browser', help='Extract cookies from the specified browser and use them in subsequent requests.')
@click.option('--threads', type=int, help="Amount of threads to use when downloading chapters.")
def _update(id_or_url: str, limit: int, browser: str, threads: int):
    """Scrape the website of the novel and update the database"""
    controllers.update(id_or_url, browser, limit, threads)


@cli.command(name='metadata')
@click.argument('id_or_url')
@click.argument('metadata_url')
def _metadata(id_or_url: str, metadata_url):
    """Import metadata from a novel metadata provider"""
    controllers.import_metadata(id_or_url, metadata_url)


@cli.command(name='list')
def _list():
    """List all novels saved in database"""
    controllers.list_novels()


@cli.command(name='info')
@click.argument('id_or_url')
def _info(id_or_url: str):
    """Show saved information of a novel"""
    controllers.show_info(id_or_url)


@cli.group(name='novel')
def _novel():
    """Manage more specific aspects of novels"""


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
