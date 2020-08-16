from tinydb import TinyDB
from tinydb.table import Table


class IAccessor:
    db: TinyDB
    table_name: str

    def __init__(self, db: TinyDB):
        self.db = db
        self._table = self.db.table(self.table_name)

    def truncate(self):
        self.table.truncate()

    @property
    def table(self) -> Table:
        return self._table
