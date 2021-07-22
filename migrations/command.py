from pathlib import Path

from alembic.command import upgrade
from alembic.config import Config


def migrate_database(dir_: Path, url_: str, config_='alembic.ini'):
    """
    :param dir_: migrations script directory
    :param url_: sqlalchemy database url
    :param config_: config
    :return:
    """
    # retrieves config file path
    config_file = dir_ / config_

    config = Config(file_=config_file)
    config.set_main_option('script_location', dir_)
    config.set_main_option('sqlalchemy.url', url_)

    # upgrade the database to the latest revision
    upgrade(config, 'head')


def migrate(url: str):
    migrate_database(Path(__file__).parent, url, 'alembic.ini')
