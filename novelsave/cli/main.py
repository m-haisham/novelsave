"""
update {only, all} [url or id]
compile {only, all} [url or id] {--formats} [--only-updated]
default: update-and-compile {only} (url or id) {--formats}
history {only, all} [url or id]
manage {config, clean, novel}
    manage novel (url or id) {add, remove} (url)
                         ... {purge}

[maybe]
periodical (--every-minutes SECONDS)
manage {startup} {add, remove}
"""
import click

from . import controllers, helpers, groups
from .. import settings
from ..containers import Application
from migrations import commands as migration_commands


def setup_logger():
    pass


def inject_dependencies():
    application = Application()
    application.config.from_dict(settings.as_dict())
    application.wire(packages=[controllers, helpers, groups])


def update_database_schema():
    migration_commands.migrate(settings.DATABASE_URL)


@click.group()
def cli():
    setup_logger()
    update_database_schema()
    inject_dependencies()
