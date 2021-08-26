"""
update {only, all} [url or id]
package {only, all} [url or id] {--formats} [--only-updated]
default: update-and-package {only} (url or id) {--formats}
history {only, all} [url or id]
_manage {config, clean, novel}
    _manage novel (url or id) {add, remove} (url)
                         ... {purge}

[maybe]
periodical (--every-minutes SECONDS)
_manage {startup} {add, remove}
"""
import json
import sys

import click
from loguru import logger

from . import controllers, helpers, groups
from ..settings import as_dict as settings_as_dict, DATABASE_URL, LOGGER_CONFIG
from ..containers import Application
from ..infrastructure.migrations import commands as migration_commands
from ..utils.helpers import config_helper


def inject_dependencies():
    application = Application()
    application.config.from_dict(settings_as_dict())

    try:
        application.config.from_dict(config_helper.from_file())
    except FileNotFoundError:
        pass

    application.wire(packages=[controllers, helpers, groups])


def update_database_schema():
    migration_commands.migrate(DATABASE_URL)


@click.group()
@click.option('--debug', is_flag=True, help="Print debugging information to console")
@logger.catch()
def cli(debug: bool):
    logger_config = LOGGER_CONFIG.copy()
    if debug:
        logger_config['handlers'][0]['level'] = 'DEBUG'

    logger.configure(**logger_config)

    update_database_schema()
    inject_dependencies()
