from tinydb import TinyDB
from tinydb.table import Table


class IAccessor:
    db: TinyDB
    table_name: str

    def __init__(self, db: TinyDB):
        self.db = db
        self._table = None

    def truncate(self):
        self.table.truncate()

    @property
    def table(self) -> Table:
        if self._table is None:
            self._table = self.db.table(self.table_name)

        return self._table
