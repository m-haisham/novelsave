import json
from pathlib import Path
from typing import List, TypeVar, Callable, Dict, Tuple

from tinydb import where

from .multi import MultiClassTable

T = TypeVar('T')


class MultiClassExternalTable(MultiClassTable):
    PATH_KEY = 'PATH'

    def __init__(
            self,
            db,
            path,
            table: str,
            cls: T,
            fields: List[str],
            identifier: str,
            naming_scheme: Callable[[T], str]
    ):
        super(MultiClassExternalTable, self).__init__(db, table, cls, fields, identifier)

        self.path = path / Path(table)
        self.path.mkdir(parents=True, exist_ok=True)

        self.naming_scheme = naming_scheme

    def insert(self, obj):
        doc, path = self._save(obj)
        self.table.insert(
            self._basic_dict(doc[self.identifier], path.relative_to(self.path))
        )

    def put(self, obj):
        doc, path = self._save(obj)
        self.table.upsert(
            self._basic_dict(doc[self.identifier], path.relative_to(self.path)),
            where(self.identifier) == doc[self.identifier]
        )

    def put_all(self, objs: List):
        for obj in objs:
            self.put(obj)

    def all(self) -> List:
        return [
            self._load(
                Path(self.path / doc[self.PATH_KEY])
            )
            for doc in self.table.all()
        ]

    def all_basic(self) -> List[T]:
        return [self._from_dict(o) for o in self.table.all()]

    def _save(self, obj) -> Tuple[Dict, Path]:
        name = self.naming_scheme(obj)
        path = self.path / Path(f'{name}.json')
        doc = self._to_dict(obj)

        with path.open('w') as f:
            json.dump(doc, f)

        return doc, path

    def _load(self, path) -> T:
        with path.open('r') as f:
            doc = json.load(f)

        return self._from_dict(doc)

    def _basic_dict(self, id, path):
        return {
            self.identifier: id,
            self.PATH_KEY: str(path)
        }