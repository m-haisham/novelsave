import click
from dependency_injector.wiring import inject
from loguru import logger

from ..controllers import get_or_create_novel
from ..main import cli


@cli.command()
@click.argument('id_or_url')
@inject
def update(
        id_or_url: str,
):
    """check and update a novel"""
    novel = get_or_create_novel(id_or_url)
    logger.info(novel)
