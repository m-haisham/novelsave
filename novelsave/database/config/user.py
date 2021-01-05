from pathlib import Path
from typing import List

from appdirs import user_config_dir

from .base import ConfigBase
from .element import ConfigElement

appname = 'Novelsave'
appauthor = 'mHaisham'


def vallidate_dir(directory):
    path = Path(directory)
    return path.exists() and path.is_dir()


class UserConfig:
    version = '2.0'

    databases: List[ConfigBase]
    configs: List[ConfigElement]

    def __init__(self):
        # get cross os configuration path
        self.path = Path(user_config_dir(appname, appauthor, self.version))
        self.path.mkdir(parents=True, exist_ok=True)
        self.config = ConfigBase(self.path, 'config.json')

        self.directory = ConfigElement(
            self.config,
            name='directory',
            default=Path.home() / Path('novels'),
            validate=vallidate_dir,
        )

        self.databases = [
            self.config
        ]

        self.configs = [
            self.directory
        ]

        self.load()

    def save(self):
        """
        write all the databases to files
        """
        for db in self.databases:
            db.save()

    def load(self):
        """
        load all the databases from file
        """
        for db in self.databases:
            db.load()
