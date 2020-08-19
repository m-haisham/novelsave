from pathlib import Path
from typing import Tuple

from tinydb import TinyDB

from .chapters import ChaptersAccess
from .info import InfoAccess
from .pending import PendingAccess
from .volumes import VolumesAccess
from ..base import DIR


class WebNovelData:
    def __init__(self, novel_id):
        # open novel
        self.db, self.path = self.open_db(novel_id)

        # set accessors
        self.info_access = InfoAccess(self.db)
        self.volumes_access = VolumesAccess(self.db)
        self.chapters_access = ChaptersAccess(self.db)
        self.pending_access = PendingAccess(self.db)

    def open_db(self, novel_id) -> Tuple[TinyDB, Path]:
        path = DIR / Path(f'n{novel_id}') / Path('data.db')
        path.parent.mkdir(parents=True, exist_ok=True)

        if not path.exists() and not path.is_file():
            with path.open('w'):
                pass

        return TinyDB(path), path
