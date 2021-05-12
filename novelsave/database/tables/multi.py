from typing import List, Iterable, Dict

from .template import ProcessedTable
from ...models import Chapter


class MultiClassTable(ProcessedTable):
    def __init__(self, db, table: str, cls, fields: List[str], identifier: str):
        super(MultiClassTable, self).__init__(db, table)

        # error checks
        if identifier not in fields:
            raise ValueError("'identifier' must be a field")
        if not fields:
            raise ValueError("'fields' must not be empty")

        self.cls = cls
        self.fields = fields
        self.identifier = identifier

    def put(self, obj):
        """
        put object with unique identifier chapter.id into database

        :param obj: object to be added
        :return: None
        """
        self.data[getattr(obj, self.identifier)] = self._to_dict(obj)
        self.flush()

    def put_all(self, objs: Iterable):
        """
        put obj with unique identifier into database

        :param objs: object to be added
        :return: None
        """
        self.data.update({getattr(obj, self.identifier): self._to_dict(obj) for obj in objs})
        self.flush()

    def all(self) -> List:
        """
        :return: all objects
        """
        return [self._from_dict(o) for o in self.data.values()]

    def get(self, id) -> Chapter:
        """
        :param id: unique identifier
        :return: chapter with corresponding id
        :raises ValueError: if more than one value corresponds to key
        """
        return self._from_dict(self.data[id])

    def remove(self, id):
        """
        removes value from pending

        :param id: id of obj to remove
        :return: None
        """
        del self.data[id]
        self.flush()

    def pre_process(self, data: List[Dict]) -> Dict:
        processed = {}

        for item in data:
            processed[item[self.identifier]] = item

        return processed

    def post_process(self, data: Dict) -> List[Dict]:
        return list(data.values())

    def _to_dict(self, obj) -> dict:
        return {field: getattr(obj, field) for field in self.fields}

    def _from_dict(self, doc) -> Chapter:
        return self.cls(**{key: value for key, value in doc.items() if key in self.fields})
