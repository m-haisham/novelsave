from pathlib import Path
from typing import Tuple

from tinydb import TinyDB

from .tables import KeyValueTable, SingleClassTable, MultiClassExternalTable, MultiClassDecoupledTable, \
    SetTable
from ..models import Novel, Chapter


class Database:
    def __init__(self, directory, create=True):
        self.db, self.path = self.open_db(directory, create)

    def open_db(self, directory, create) -> Tuple[TinyDB, Path]:
        path = directory / Path('data') / Path('meta.db')

        if not path.exists() or not path.is_file():
            if create:
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.is_file():
                    with path.open('w'):
                        pass
            else:
                raise FileNotFoundError(f'{path} does not exist')

        return TinyDB(path), path


class NovelData(Database):
    def __init__(self, directory, create=True, load_chapters=True):
        super(NovelData, self).__init__(directory, create)

        self.novel = SingleClassTable(self.db, 'novel', Novel,
                                      ['title', 'author', 'synopsis', 'thumbnail', 'lang', 'meta_source', 'url'])
        self.metadata = SetTable(self.db, 'metadata', field1='name', field2='value')
        self.pending = MultiClassDecoupledTable(self.db, self.path.parent, 'pending', Chapter,
                                                ['index', 'volume', 'url'], 'url')
        self.chapters = MultiClassExternalTable(
            self.db, self.path.parent, 'chapters',
            Chapter, ['index', 'title', 'paragraphs', 'volume', 'url'], 'url',
            naming_scheme=lambda c: str(c.index).zfill(4),
            load=load_chapters
        )
        self.misc = KeyValueTable(self.db, 'misc')

    def close(self):
        self.pending.decoupled_db.close()
        self.db.close()
