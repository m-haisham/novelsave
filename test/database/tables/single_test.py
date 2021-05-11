import unittest
from dataclasses import dataclass

from novelsave.database.template import Database
from novelsave.database.tables import SingleClassTable


@dataclass
class TestClass:
    id: int = None
    name: str = None
    subject: str = None
    other: str = None


class TestSingleClassTest(unittest.TestCase):
    db: Database
    table: SingleClassTable

    table_name = 'single_class_test_table'
    fields = ['id', 'name', 'subject']

    data = TestClass(
        id=1,
        name='name',
        subject='subject',
        other='not important',
    )

    def setUp(self) -> None:
        self.db = Database(':memory:')
        self.table = SingleClassTable(self.db, self.table_name, TestClass, self.fields)

    def test_set(self):
        self.table.set(self.data)
        saved = self.db.get_table(self.table_name)

        _data = vars(self.data)
        del _data['other']

        self.assertDictEqual(_data, saved)

    def test_parse(self):
        self.table.set(self.data)

        data = self.table.parse()

        self.assertIsInstance(data, TestClass)
        self.assertEqual(data.name, self.data.name)
        self.assertEqual(data.id, self.data.id)
        self.assertEqual(data.subject, self.data.subject)
        self.assertIsNone(data.other)
