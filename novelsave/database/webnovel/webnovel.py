from .info import InfoAccess
from .volumes import VolumesAccess
from ..base import Database
from ..tables import KeyValueTable, MultiClassTable, MultiClassExternalTable
from ...models import Chapter


class WebNovelData(Database):
    def __init__(self, directory):
        super(WebNovelData, self).__init__(directory)

        # set accessors
        self.info = InfoAccess(self.db)
        self.volumes = VolumesAccess(self.db)
        self.pending = MultiClassTable(self.db, 'pending', Chapter, ['index', 'no', 'url'], 'url')
        self.chapters = MultiClassExternalTable(
            self.db, self.path.parent, 'chapters', Chapter,
            ['index', 'no', 'title', 'paragraphs', 'url'], 'url',
            naming_scheme=lambda c: str(c.index),
        )
        self.misc = KeyValueTable(self.db, 'misc')
