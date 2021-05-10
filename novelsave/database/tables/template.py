from typing import Dict, Union, List

from ..template import Database

Serializable = Union[Dict, List]


class Table:
    def __init__(self, db: Database, table: str):
        self.db = db
        self.table = table
        self.default = lambda: {}

    @property
    def data(self) -> Serializable:
        return self.db.get_table(self.table, self.default())

    @data.setter
    def data(self, data: Serializable):
        self.db.set_table(self.table, data)
        self.db.save()

    def save(self):
        self.db.save()

    def truncate(self):
        self.data = self.default()
