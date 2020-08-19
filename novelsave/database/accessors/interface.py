from tinydb import TinyDB
from tinydb.table import Table


class IAccessor:
    db: TinyDB
    _table_name: str

    def __init__(self, db: TinyDB):
        self.db = db
        self._table = self.db.table(self._table_name)

    def truncate(self):
        self.table.truncate()

    @property
    def table_name(self):
        return self._table_name

    @table_name.setter
    def table_name(self, name):
        self._table = self.db.table(name)
        self._table_name = name

    @property
    def table(self) -> Table:
        return self._table
