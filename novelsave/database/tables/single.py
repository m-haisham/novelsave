from typing import List

from .keyvalue import KeyValueTable


class SingleClassTable(KeyValueTable):
    def __init__(self, db, table: str, cls, fields: List[str]):
        super(SingleClassTable, self).__init__(db, table)

        self.cls = cls
        self.fields = fields

    def set(self, values):
        self.data = {field: getattr(values, field) for field in self.fields}

    def parse(self):
        return self.cls(**{key: value for key, value in self.data.items() if key in self.fields})
