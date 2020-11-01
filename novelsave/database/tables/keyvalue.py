from ..accessors import KeyValueAccessor


class KeyValueTable(KeyValueAccessor):
    def __init__(self, db, table):
        super(KeyValueTable, self).__init__(db)
        self.table_name = table
