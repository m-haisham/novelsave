import click
from dependency_injector.wiring import inject

from .. import controllers
from ..main import cli


@cli.command()
@click.argument('id_or_url')
@inject
def update(
        id_or_url: str,
):
    """check and update a novel"""
    controllers.update(id_or_url, True)
