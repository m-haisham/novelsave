import atexit

from pathlib import Path
from typing import Tuple

from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from .tables import SingleClassTable, SequenceTable, MultiClassTable
from ..models import Novel, Chapter


class Database:
    def __init__(self, directory):
        self.db, self.path = self.open_db(directory)

    def open_db(self, directory) -> Tuple[TinyDB, Path]:
        path = directory / Path('data.db')
        path.parent.mkdir(parents=True, exist_ok=True)

        if not path.exists() and not path.is_file():
            with path.open('w'):
                pass

        return TinyDB(path), path


class NovelData(Database):
    def __init__(self, directory):
        super(NovelData, self).__init__(directory)

        self.novel = SingleClassTable(self.db, 'novel', Novel, ['title', 'author', 'thumbnail', 'url'])
        self.pending = SequenceTable(self.db, 'pending', key='url')
        self.chapters = MultiClassTable(self.db, 'chapters', Chapter,
                                        ['index', 'no', 'title', 'paragraphs', 'url', 'bulk'], 'url')
