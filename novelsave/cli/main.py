import functools

import click
from loguru import logger
from tqdm import tqdm

from . import controllers, helpers, groups
from ..containers import Application
from ..infrastructure.migrations import commands as migration_commands
from ..settings import config, DATABASE_URL, LOGGER_CONFIG
from ..utils.helpers import config_helper


def inject_dependencies():
    application = Application()
    application.config.from_dict(config)

    try:
        application.config.from_dict(config_helper.from_file())
    except FileNotFoundError:
        pass

    application.wire(packages=[controllers, helpers, groups])


def update_database_schema():
    migration_commands.migrate(DATABASE_URL)


@click.group()
@click.option('--debug', is_flag=True, help="Print debugging information to console")
@click.option('--plain', is_flag=True, help="Disable reactive and interactive elements")
def cli(debug: bool, plain: bool):
    logger_config = LOGGER_CONFIG.copy()
    if debug:
        logger_config['handlers'][0]['level'] = 'DEBUG'
    if plain:
        tqdm.__init__ = functools.partialmethod(tqdm.__init__, disable=True)

    logger.configure(**logger_config)

    update_database_schema()
    inject_dependencies()


@logger.catch()
def main():
    cli()
