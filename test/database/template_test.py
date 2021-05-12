import unittest

from novelsave.database.template import DatabaseTemplate


class TestDatabaseTemplate(unittest.TestCase):
    dbt: DatabaseTemplate
    table_name = 'test_database_template_table'

    data = {'name': 'this', 'other': '2'}

    def setUp(self) -> None:
        self.dbt = DatabaseTemplate('')

    def test_get_table(self):
        self.dbt._data[self.table_name] = dict(self.data)

        data = self.dbt.get_table(self.table_name)
        self.assertDictEqual(data, self.data)

    def test_get_table_nonexistent(self):
        with self.assertRaises(KeyError):
            self.dbt.get_table(self.table_name)

    def test_set_table(self):
        self.dbt.set_table(self.table_name, dict(self.data))

        data = self.dbt._data[self.table_name]
        self.assertDictEqual(self.data, data)