import unittest
from dataclasses import dataclass

from novelsave.database.tables import MultiClassTable
from novelsave.database.template import Database


@dataclass
class TestClass:
    id: int = None
    name: str = None
    subject: str = None
    other: str = None

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name and self.subject == other.subject


class TestMultiClassTable(unittest.TestCase):
    db: Database
    table: MultiClassTable

    table_name = 'multi_test_table'

    tc1 = TestClass(
        id=1,
        name='nm1',
        subject='sb1',
        other='not 1important',
    )

    tc2 = TestClass(
        id=2,
        name='nm2',
        subject='sb2',
        other='not 2important',
    )

    tc1c = TestClass(
        id=1,
        name='nm1-conflict',
        subject='sb1',
        other='not 1important',
    )

    fields = ['id', 'name', 'subject']

    def setUp(self) -> None:
        self.db = Database(':memory:')
        self.table = MultiClassTable(self.db, self.table_name, TestClass, self.fields, 'id')

    def test_insert(self):
        self.table.insert(self.tc1)

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, dict)
        self.assertEqual(1, len(data))
        self.assertEqual(self.tc1, TestClass(**data[1]))

    def test_insert_conflict(self):
        self.table.insert(self.tc1)
        with self.assertRaises(ValueError):
            self.table.insert(self.tc1c)

    def test_put(self):
        self.table.put(self.tc1)

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, dict)
        self.assertEqual(1, len(data))
        self.assertEqual(self.tc1, TestClass(**data[self.tc1.id]))

    def test_put_conflict(self):
        self.table.put(self.tc1)
        self.table.put(self.tc1c)

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, dict)
        self.assertEqual(1, len(data))
        self.assertEqual(self.tc1c, TestClass(**data[self.tc1.id]))

    def test_put_all(self):
        self.table.put_all([self.tc1, self.tc2])

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, dict)
        self.assertEqual(2, len(data))

    def test_put_all_duplicate(self):
        self.table.put_all([self.tc1, self.tc1c])

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, dict)
        self.assertEqual(1, len(data))

    def test_put_all_conflict(self):
        self.table.put_all([self.tc1, self.tc2])
        self.table.put_all([self.tc1c])

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, dict)
        self.assertEqual(2, len(data))

    def test_get(self):
        self.table.insert(self.tc1)

        data = self.db._data[self.table_name]
        self.assertIsInstance(data, dict)
        self.assertEqual(1, len(data))
        self.assertEqual(self.tc1, self.table.get(1))

    def test_remove(self):
        self.table.insert(self.tc1)
        self.table.remove(self.tc1.id)

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, dict)
        self.assertEqual(0, len(data))

    def test_all(self):
        self.table.insert(self.tc1)
        self.table.insert(self.tc2)

        data = self.table.all()

        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))
        self.assertIn(self.tc1, data)
        self.assertIn(self.tc2, data)
