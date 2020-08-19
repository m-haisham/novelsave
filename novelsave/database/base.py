from pathlib import Path

from tinydb import TinyDB

from .tables import KeyValueTable, SequenceTable
from .file import slugify
from ..models import Novel

DIR = Path.home() / Path('novels')


class NovelBase:
    def __init__(self, url):
        self.db = self.open_db(url)

        self.novel = KeyValueTable(self.db, 'novel', Novel, ['title', 'author', 'thumbnail', 'url'])
        self.pending = SequenceTable(self.db, 'pending')

    def open_db(self, url) -> TinyDB:
        folder_name = slugify(url.split('/')[-1])

        path = DIR / Path(folder_name) / Path('data.db')
        path.parent.mkdir(parents=True, exist_ok=True)

        if not path.exists() and not path.is_file():
            with path.open('w'):
                pass

        return TinyDB(path)