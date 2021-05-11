from pathlib import Path
from typing import Optional

from .template import Table
from ..template import FileDatabase


class Decoupled:
    """
    This is a modification class to be applied to tables.
    When applied, the table is extracted to another file

    The primary use case of the class is to separate highly variable (table that changes often)
    from other tables which may no be as variable
    """

    def __new__(cls, table: Table, path: Optional[Path] = None) -> Table:
        new_path = table.db.path / (path or f'{table.table}.db')
        assert new_path.is_file()

        table.db = FileDatabase(new_path, should_create=True)

        return table
