from pathlib import Path
from typing import Tuple, List

from appdirs import user_config_dir
from tinydb import TinyDB

from .element import ConfigElement
from ..tables import KeyValueTable
from ...tools import UiTools

appname = 'NovelSave'
appauthor = 'mHaisham'


def vallidate_dir(directory):
    path = Path(directory)
    return path.exists() and path.is_dir()


class UserConfig:
    version = '1.0'

    configs: List[ConfigElement]

    def __init__(self):
        # get cross os configuration path
        self.path = Path(user_config_dir(appname, appauthor, self.version))
        self.db, self.table = self.open_db(self.path)

        self.directory = ConfigElement(
            self.table,
            'directory',
            default=Path.home() / Path('novels'),
            validate=vallidate_dir,
        )

        self.configs = [
            self.directory
        ]

    def open_db(self, directory) -> Tuple[TinyDB, KeyValueTable]:
        directory.mkdir(parents=True, exist_ok=True)
        db = TinyDB(directory / Path('config.json'))

        return db, KeyValueTable(db, 'config')

    def print_configs(self):
        for config in self.configs:
            UiTools.print_var(config.name, config.get())
