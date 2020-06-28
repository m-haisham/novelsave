from pathlib import Path

from tinydb import TinyDB
from .accessors import InfoAccess, VolumesAccess, ChaptersAccess, PendingAccess

DIR = Path('novels')


class NovelData:
    def __init__(self, novel_id):
        # open novel
        self.db = self.open_db(novel_id)

        # set accessors
        self.info_access = InfoAccess(self.db)
        self.volumes_access = VolumesAccess(self.db)
        self.chapters_access = ChaptersAccess(self.db)
        self.pending_access = PendingAccess(self.db)

    def open_db(self, novel_id) -> TinyDB:
        path = self._novel_path(novel_id)
        path.parent.mkdir(parents=True, exist_ok=True)

        if not path.exists() and not path.is_file():
            with path.open('w'):
                pass

        return TinyDB(path)

    def _novel_path(self, novel_id):
        return DIR / Path(f'n{novel_id}') / Path('data.db')
