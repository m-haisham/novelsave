from pathlib import Path

from .template import FileDatabase
from .tables import KeyValueTable, SingleClassTable, MultiClassExternalTable, MultiClassTable, Decoupled, \
    SetTable
from ..models import Novel, Chapter


class NovelData(FileDatabase):
    def __init__(self, directory, should_create=True, load_chapters=True):
        super(NovelData, self).__init__(Path(directory) / Path('data') / 'meta.db', should_create)

        self.novel = SingleClassTable(self, 'novel', Novel,
                                      ['title', 'author', 'synopsis', 'thumbnail', 'lang', 'meta_source', 'url'])
        self.metadata = SetTable(self, 'metadata', ['name', 'value'])
        self.pending = Decoupled(
            MultiClassTable(self, 'pending', Chapter, ['index', 'title', 'volume', 'url'], 'url'),
        )
        self.chapters = MultiClassExternalTable(
            self, self.path, 'chapters',
            Chapter, ['index', 'title', 'paragraphs', 'volume', 'url'], 'url',
            naming_scheme=lambda c: str(c.index).zfill(4),
            load=load_chapters
        )
        self.misc = KeyValueTable(self, 'misc')
