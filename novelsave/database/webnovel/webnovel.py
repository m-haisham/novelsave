from pathlib import Path
from typing import Tuple

from tinydb import TinyDB

from .chapters import ChaptersAccess
from .info import InfoAccess
from .pending import PendingAccess
from .volumes import VolumesAccess


class WebNovelData:
    def __init__(self, directory):
        # open novel
        self.db, self.path = self.open_db(directory)

        # set accessors
        self.info_access = InfoAccess(self.db)
        self.volumes_access = VolumesAccess(self.db)
        self.chapters_access = ChaptersAccess(self.db)
        self.pending_access = PendingAccess(self.db)

    def open_db(self, directory) -> Tuple[TinyDB, Path]:
        path = directory / Path('data.db')
        path.parent.mkdir(parents=True, exist_ok=True)

        if not path.exists() and not path.is_file():
            with path.open('w'):
                pass

        return TinyDB(path), path
