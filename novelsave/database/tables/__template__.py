from typing import Dict

from ..__template__ import Database


class Table:
    def __init__(self, db: Database, table: str):
        self.db = db
        self.table = table

    @property
    def data(self) -> Dict:
        return self.db.get_table(self.table)

    @data.setter
    def data(self, data: Dict):
        self.db.set_table(self.table, data)
