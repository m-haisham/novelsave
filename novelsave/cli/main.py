"""
update {only, all} [url or id]
compile {only, all} [url or id] {--formats} [--only-updated]
default: update-and-compile {only} (url or id) {--formats}
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
from .. import settings
from ..containers import Application
from ..infrastructure.migrations import commands as migration_commands
from ..utils.helpers import config_helper


def inject_dependencies():
    application = Application()
    application.config.from_dict(settings.as_dict())

    try:
        application.config.from_dict(config_helper.from_file())
    except FileNotFoundError:
        pass

    application.wire(packages=[controllers, helpers, groups])


def update_database_schema():
    migration_commands.migrate(settings.DATABASE_URL)


@click.group()
@logger.catch()
def cli():
    logger.configure(**settings.LOGGER_CONFIG)
    update_database_schema()
    inject_dependencies()
