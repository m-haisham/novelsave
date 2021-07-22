from typing import Dict, Union, List, Callable

from ..template import DatabaseTemplate

Serializable = Union[Dict, List]


class Table:
    """
    TODO
    - should hold the changes until saved: flush()
    - apply post processing before applying to main dict
    """

    def __init__(self, db: DatabaseTemplate, table: str, default_factory: Callable[[], Serializable] = lambda: {}):
        self.db = db
        self.table = table
        self.default_factory = default_factory

    @property
    def data(self) -> Serializable:
        try:
            return self.db.get_table(self.table)
        except KeyError:
            return self.db.set_table(self.table, self.default_factory())

    @data.setter
    def data(self, data: Serializable):
        self.db.set_table(self.table, data)
        self.db.save()

    def flush(self):
        self.db.save()

    def truncate(self):
        self.data = self.default_factory()


class ProcessedTable(Table):
    def __init__(self, db: DatabaseTemplate, table: str, default_factory: Callable[[], Serializable] = lambda: {}):
        super(ProcessedTable, self).__init__(db, table, default_factory)
        self._buffer = None

    @property
    def data(self) -> Serializable:
        if self._buffer is None:
            try:
                data = self.db.get_table(self.table)
            except KeyError:
                data = self.db.set_table(self.table, self.default_factory())

            self._buffer = self.pre_process(data)

        return self._buffer

    @data.setter
    def data(self, data: Serializable):
        self._buffer = data

    def flush(self):
        self.db.set_table(self.table, self.post_process(self._buffer))
        self.db.save()

    def truncate(self):
        self.data = self.default_factory()

    def pre_process(self, data):
        return data

    def post_process(self, data):
        return data
