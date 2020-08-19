from pathlib import Path
from typing import Tuple

from tinydb import TinyDB

from .file import slugify
from .tables import SingleClassTable, SequenceTable, MultiClassTable
from ..models import Novel, Chapter

DIR = Path.home() / Path('novels')


class NovelData:
    def __init__(self, url):
        self.db, self.path = self.open_db(url)

        self.novel = SingleClassTable(self.db, 'novel', Novel, ['title', 'author', 'thumbnail', 'url'])
        self.pending = SequenceTable(self.db, 'pending', key='url')
        self.chapters = MultiClassTable(self.db, 'chapters', Chapter, ['no', 'title', 'paragraphs', 'url'], 'url')

    def open_db(self, url) -> Tuple[TinyDB, Path]:
        # trailing slash adds nothing
        if url[-1] == '/':
            url = url[:-1]

        folder_name = slugify(url.split('/')[-1])

        path = DIR / Path(folder_name) / Path('data.db')
        path.parent.mkdir(parents=True, exist_ok=True)

        if not path.exists() and not path.is_file():
            with path.open('w'):
                pass

        return TinyDB(path), path
