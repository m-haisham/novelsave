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
            basic_fields: List[str],
            identifier: str,
            naming_scheme: Callable[[T], str],
            on_missing: Callable[[T], None] = None,
    ):
        super(MultiClassExternalTable, self).__init__(db, table, cls, fields, identifier)

        # these are used to denote which fields to save in table
        self.basic_fields = set(basic_fields + [self.identifier])

        self.path = path / Path(table)
        self.path.mkdir(parents=True, exist_ok=True)

        self.naming_scheme = naming_scheme
        self.on_missing = on_missing

    def insert(self, obj):
        doc, path = self._save(obj)
        self.table.insert(
            self._basic_dict(obj, path.relative_to(self.path))
        )

    def put(self, obj):
        doc, path = self._save(obj)
        self.table.upsert(
            self._basic_dict(obj, path.relative_to(self.path)),
            where(self.identifier) == doc[self.identifier]
        )

    def put_all(self, objs: List):
        for obj in objs:
            self.put(obj)

    def all(self) -> List:
        """
        :return: return full data, including from the external files
        """
        objs = []
        for doc in self.table.all():

            try:
                obj = self._load(
                    Path(self.path / doc[self.PATH_KEY])
                )
            # if file doesnt exist or file is not proper json
            except (FileNotFoundError, json.JSONDecodeError):
                self.remove(doc[self.identifier])

                # external file missing callback
                if self.on_missing is not None:
                    self.on_missing(self._from_dict(doc))
                continue

            objs.append(obj)

        return objs

    def check(self):
        """
        Checks whether all the external files exist
        entries that doesnt have the external file are removed from table

        :return: whether all the external files exist
        """
        for doc in self.table.all():
            path = self.path / doc[self.PATH_KEY]

            # if file doesnt exist
            if not path.exists() or not path.is_file():
                # remove basic dict from this table
                self.remove(doc[self.identifier])

                # external file missing callback
                if self.on_missing is not None:
                    self.on_missing(self._from_dict(doc))

    def all_basic(self) -> List[T]:
        """
        :return: basic information that is stored inside the table; without reading external files
        """
        return [self._from_dict(o) for o in self.table.all()]

    def _save(self, obj) -> Tuple[Dict, Path]:
        """
        save path: self.path / table_name / [file]

        :param obj: object to be saved
        :return: saves the object in json as per naming scheme
        """
        name = self.naming_scheme(obj)
        path = self.path / Path(f'{name}.json')
        doc = self._to_dict(obj)

        with path.open('w') as f:
            json.dump(doc, f)

        return doc, path

    def _load(self, path) -> T:
        """
        :param path: path to load the the object from
        :return: reads and converts the json to [cls]
        """
        with path.open('r') as f:
            doc = json.load(f)

        return self._from_dict(doc)

    def _basic_dict(self, obj, path):
        """
        :param obj: object to be saved
        :param path: path where the external file is saved
        :return: basic dict which should be stored in main table
        """
        basic = {field: getattr(obj, field) for field in self.basic_fields}
        basic[self.PATH_KEY] = str(path)

        return basic
