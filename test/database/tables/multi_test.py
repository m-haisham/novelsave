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

    def test_pre_process(self):
        test_data = [
            vars(self.tc1),
            vars(self.tc2),
        ]

        processed_data = self.table.pre_process(test_data)

        self.assertIsInstance(processed_data, dict)
        self.assertEqual(2, len(processed_data))
        self.assertDictEqual(vars(self.tc1), processed_data[self.tc1.id])
        self.assertDictEqual(vars(self.tc2), processed_data[self.tc2.id])

    def test_pre_process_dict_format(self):
        test_data = {
            self.tc1.id: vars(self.tc1),
            self.tc2.id: vars(self.tc2),
        }

        processed_data = self.table.pre_process(test_data)

        self.assertIsInstance(processed_data, dict)
        self.assertEqual(2, len(processed_data))
        self.assertDictEqual(test_data, processed_data)

    def test_post_process(self):
        test_data = {
            self.tc1.id: vars(self.tc1),
            self.tc2.id: vars(self.tc2),
        }

        processed_data = self.table.post_process(test_data)

        self.assertIsInstance(processed_data, list)
        self.assertEqual(2, len(processed_data))
        self.assertDictEqual(vars(self.tc1), processed_data[0])
        self.assertDictEqual(vars(self.tc2), processed_data[1])

    def test_process_cycle(self):
        test_data = [
            vars(self.tc1),
            vars(self.tc2),
        ]

        pre_processed = self.table.pre_process(test_data)
        post_processed = self.table.post_process(pre_processed)

        for i in range(len(test_data)):
            self.assertDictEqual(test_data[i], post_processed[i])

    def test_put(self):
        self.table.put(self.tc1)

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))
        self.assertEqual(self.tc1, TestClass(**data[0]))

    def test_put_conflict(self):
        self.table.put(self.tc1)
        self.table.put(self.tc1c)

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))
        self.assertEqual(self.tc1c, TestClass(**data[0]))

    def test_put_all(self):
        self.table.put_all([self.tc1, self.tc2])

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))

    def test_put_all_duplicate(self):
        self.table.put_all([self.tc1, self.tc1c])

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))

    def test_put_all_conflict(self):
        self.table.put_all([self.tc1, self.tc2])
        self.table.put_all([self.tc1c])

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))

    def test_get(self):
        self.table.put(self.tc1)

        data = self.db._data[self.table_name]
        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))
        self.assertEqual(self.tc1, self.table.get(1))

    def test_get_default(self):
        self.assertIsNone(self.table.get('missing'))
        self.assertEqual('default', self.table.get('missing', 'default'))

    def test_remove(self):
        self.table.put(self.tc1)
        self.table.remove(self.tc1.id)

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, list)
        self.assertEqual(0, len(data))

    def test_remove_nonexistent(self):
        self.table.remove('something')

    def test_all(self):
        self.table.put(self.tc1)
        self.table.put(self.tc2)

        data = self.table.all()

        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))
        self.assertIn(self.tc1, data)
        self.assertIn(self.tc2, data)
