import json
from pathlib import Path
from typing import List

from appdirs import user_config_dir

from .element import ConfigElement
from ...logger import NovelLogger

appname = 'Novelsave'
appauthor = 'mHaisham'


def vallidate_dir(directory):
    path = Path(directory)
    return path.exists() and path.is_dir()


class UserConfig:
    version = '2.0'

    configs: List[ConfigElement]

    def __init__(self):
        # get cross os configuration path
        self.path = Path(user_config_dir(appname, appauthor, self.version))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = {}
        self.load()

        self.directory = ConfigElement(
            self,
            name='directory',
            default=Path.home() / Path('novels'),
            validate=vallidate_dir,
        )

        self.configs = [
            self.directory
        ]

    def save(self):
        with self.path.open('w') as f:
            json.dump(self.data, f)

    def load(self):
        try:
            with self.path.open('r') as f:
                self.data = json.load(f)

        # log decoding error
        except json.JSONDecodeError as e:
            with self.path.open('r') as f:
                data = f.read()

            NovelLogger.instance.logger.error(f'{data} - {repr(e)}')

        # treat as empty
        except FileNotFoundError:
            pass