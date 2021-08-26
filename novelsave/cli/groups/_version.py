from loguru import logger

from ..main import cli
from ... import __version__


@cli.command(name='version')
def _version():
    """Show application version"""
    logger.info(__version__)
