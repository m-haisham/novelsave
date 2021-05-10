import unittest

from novelsave.database.tables import KeyValueTable
from novelsave.database.template import Database


class TestKeyValueTable(unittest.TestCase):
    db: Database
    table: KeyValueTable

    table_name = 'keyvalue_test_table'

    def setUp(self) -> None:
        self.db = Database(':memory:')
        self.table = KeyValueTable(self.db, self.table_name)

    def test_put(self):
        self.table.put('key', 'value')

        data = self.db._data[self.table_name]

        self.assertEqual(1, len(data))
        self.assertEqual(data['key'], 'value')

    def test_get(self):
        self.db._data[self.table_name] = {}
        self.db._data[self.table_name]['key'] = 'value'

        self.assertEqual('value', self.table.get('key'))

    def test_get_default(self):
        self.assertEqual('default', self.table.get('key', 'default'))

    def test_remove(self):
        self.db._data[self.table_name] = {}
        self.db._data[self.table_name]['key'] = 'value'

        self.table.remove('key')

        self.assertEqual(0, len(self.db._data[self.table_name]))

    def test_remove_nonexistent(self):
        with self.assertRaises(KeyError):
            self.table.remove('key')

    def test_all(self):
        d = {'key': 'value', 'key1': 'value1', 'key2': 'value2'}
        self.db._data[self.table_name] = dict(d)

        data = self.table.all()
        self.assertDictEqual(d, data)
