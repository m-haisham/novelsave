import click

from .. import controllers
from ..main import cli


@cli.command(name='compile')
@click.argument('id_or_url')
def _compile(id_or_url: str):
    controllers.compile(id_or_url)
