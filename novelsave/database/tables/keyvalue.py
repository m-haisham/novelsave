from typing import List, overload

from ..accessors import KeyValueAccessor


class KeyValueTable(KeyValueAccessor):
    def __init__(self, db, table: str, cls, fields: List[str]):
        super(KeyValueTable, self).__init__(db)

        self.table_name = table
        self.cls = cls
        self.fields = fields

    def set(self, values):
        for field in self.fields:
            self.put(field, getattr(values, field))

    def parse(self):
        return self.cls(**{key: value for key, value in self.all().items() if key in self.fields})