import atexit
import functools
import sys

import click
from loguru import logger
from tqdm import tqdm

from . import controllers, helpers, groups, events
from .events import update_check_event
from .. import __version__
from ..containers import Application
from ..exceptions import NSError
from ..migrations import commands as migration_commands
from ..settings import config, DATABASE_URL, LOGGER_CONFIG
from ..utils.helpers import config_helper


def inject_dependencies():
    application = Application()
    application.config.from_dict(config)

    try:
        application.config.from_dict(config_helper.from_file())
    except FileNotFoundError:
        pass

    application.wire(modules=[events], packages=[controllers, helpers, groups])


def update_database_schema():
    migration_commands.migrate(DATABASE_URL)


@click.group()
@click.version_option(__version__)
@click.option('-d', '--debug', is_flag=True, help="Print debugging information to console.")
@click.option('-p', '--plain', is_flag=True, help="Disable reactive and interactive elements.")
@click.option('-s', '--skip-updates', is_flag=True, help="Dont check for updates at the end of program.")
def cli(debug: bool, plain: bool, skip_updates: bool):
    logger_config = LOGGER_CONFIG.copy()
    if debug:
        logger_config['handlers'][0]['level'] = 'DEBUG'
    if plain:
        tqdm.__init__ = functools.partialmethod(tqdm.__init__, disable=True)

    logger.configure(**logger_config)

    update_database_schema()
    inject_dependencies()

    # only check for updates if this is not a help call
    if '--help' not in sys.argv[1:] and not skip_updates:
        atexit.register(update_check_event)


@logger.catch()
def main():
    try:
        cli()
    except NSError as e:
        logger.exception(e)
        sys.exit(1)
