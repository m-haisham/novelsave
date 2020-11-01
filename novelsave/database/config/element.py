from typing import Callable, Any

from ..tables import KeyValueTable


class ConfigElement:
    name: str
    table: KeyValueTable
    default: Any
    validate: Callable[[Any], bool]

    def __init__(self, table, name, default=None, validate=None):
        self.table = table
        self.name = name
        self.default = default
        self.validate = validate

    def get(self):
        return self.table.get(self.name, self.default)

    def put(self, value):
        valid = True
        if self.validate is not None:
            valid = self.validate(value)

        if valid:
            self.table.put(self.name, value)
        else:
            raise ValueError(f"Validation Failed; '{value}' is invalid for config '{self.name}'")
