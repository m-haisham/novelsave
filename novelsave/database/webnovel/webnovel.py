import atexit
from pathlib import Path
from typing import Tuple

from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from .chapters import ChaptersAccess
from .info import InfoAccess
from .pending import PendingAccess
from .volumes import VolumesAccess
from ..base import Database


class WebNovelData(Database):
    def __init__(self, directory):
        super(WebNovelData, self).__init__(directory)

        # set accessors
        self.info_access = InfoAccess(self.db)
        self.volumes_access = VolumesAccess(self.db)
        self.chapters_access = ChaptersAccess(self.db)
        self.pending_access = PendingAccess(self.db)