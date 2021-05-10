from typing import Dict, Union, List, Callable

from ..template import DatabaseTemplate

Serializable = Union[Dict, List]


class Table:
    def __init__(self, db: DatabaseTemplate, table: str, default_factory: Callable[[], Serializable] = lambda: {}):
        self.db = db
        self.table = table
        self.default_factory = default_factory

    @property
    def data(self) -> Serializable:
        try:
            return self.db.get_table(self.table)
        except KeyError:
            self.db.set_table(self.table, self.default_factory())
            return self.db.get_table(self.table)

    @data.setter
    def data(self, data: Serializable):
        self.db.set_table(self.table, data)
        self.db.save()

    def save(self):
        self.db.save()

    def truncate(self):
        self.data = self.default_factory()
