import click

from .. import controllers
from ..main import cli


@cli.group(name='manage')
def _manage():
    """group of database commands"""
