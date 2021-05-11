import unittest

from novelsave.database.tables import SetTable
from novelsave.database.template import Database


class TestSetSequenceTable(unittest.TestCase):
    db: Database
    table: SetTable

    table_name = 'set_sequence_test_table'

    d1 = {
        'id': 'id1',
        'name': 'nm1',
        'subject': 'sb1',
    }

    d2 = {
        'id': 'id2',
        'name': 'nm2',
        'subject': 'sb2',
    }

    d1c = {
        'id': 'id1',
        'name': 'nm1',
        'subject': 'sb1-conflict',
    }

    def setUp(self) -> None:
        self.db = Database(':memory:')
        self.table = SetTable(self.db, self.table_name, ['id', 'name'])

    def test_put(self):
        self.table.put(dict(self.d1))

        data = self.db._data[self.table_name]

        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))
        self.assertDictEqual(self.d1, data[0])

    def test_put_incomplete_data(self):
        with self.assertRaises(KeyError):
            self.table.put({'id': 'as'})

        with self.assertRaises(KeyError):
            self.table.put({'name': 'as'})

    def test_put_conflict(self):
        self.table.put(dict(self.d1))

        # test initial put
        data = self.db._data[self.table_name]

        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))

        self.table.put(dict(self.d1c))

        self.assertEqual(1, len(data))
        self.assertDictEqual(self.d1c, data[0])

    def test_remove_partial(self):
        self.table.put(dict(self.d1))
        self.table.put(dict(self.d2))

        # test initial put
        data = self.db._data[self.table_name]
        self.assertEqual(2, len(data))

        with self.assertRaises(KeyError):
            self.table.remove({'id': 'id1'})
        self.assertEqual(2, len(data))

        with self.assertRaises(KeyError):
            self.table.remove({'name': 'nm2'})
        self.assertEqual(2, len(data))

    def test_remove(self):
        self.table.put(dict(self.d1))
        self.table.put(dict(self.d2))

        # test initial put
        data = self.db._data[self.table_name]
        self.assertEqual(2, len(data))

        self.table.remove({'id': 'id1', 'name': 'nm1'})
        self.assertEqual(1, len(data))

    def test_all(self):
        self.table.put(dict(self.d1))
        self.table.put(dict(self.d2))

        data = self.table.all()
        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))

    def test_search_where(self):
        self.table.put(dict(id='something', name='this'))
        self.table.put(dict(id='ad', name='is'))
        self.table.put(dict(id='ad', name='a'))
        self.table.put(dict(id='ad', name='name'))
        self.table.put(dict(id='this', name='.',))
        self.table.put(dict(id='this', name='a'))

        results = self.table.search_where('id', 'ad')

        self.assertEqual(3, len(results))

    def test_remove_where(self):
        self.table.put(dict(id='something', name='this'))
        self.table.put(dict(id='ad', name='is'))
        self.table.put(dict(id='ad', name='a'))
        self.table.put(dict(id='ad', name='name'))
        self.table.put(dict(id='this', name='.',))
        self.table.put(dict(id='this', name='a'))

        self.table.remove_where('name', 'a')

        data = self.db._data[self.table_name]
        self.assertEqual(4, len(data))
