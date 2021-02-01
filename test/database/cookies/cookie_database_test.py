import time
import unittest
from datetime import datetime

from requests.cookies import RequestsCookieJar

from novelsave.database import CookieDatabase
from novelsave.database.cookies import DuplicateCookieError


class TestCookieDatabase(unittest.TestCase):
    def setUp(self) -> None:
        self.cookies = CookieDatabase(':memory:')

    def test_search_one(self):
        # prepare data
        data = [
            ('name', 'value', 'domain1', 'path1', int(time.time())),
            ('name', 'value', 'domain2', 'path1', int(time.time())),
            ('name2', 'value', 'domain2', 'path1', int(time.time())),
            ('name2', 'value', 'domain3', 'path1', int(time.time())),
        ]
        self.cookies.insert(data)

        # get cookies
        cookies = self.cookies.select('domain2')

        # check for same length
        self.assertEqual(2, len(cookies))

        # check for same data
        filtered_data = [c for c in data if c[2] == 'domain2']
        for c in cookies:
            self.assertIn(tuple(c.values()), filtered_data)

    def test_search_many(self):
        # prepare data
        data = [
            ('name', 'value', 'domain1', 'path1', int(time.time())),
            ('name', 'value', 'domain2', 'path1', int(time.time())),
            ('name2', 'value', 'domain2', 'path1', int(time.time())),
            ('name2', 'value', 'domain3', 'path1', int(time.time())),
            ('name3', 'value', 'domain3', 'path1', int(time.time())),
            ('name4', 'value', 'domain3', 'path1', int(time.time())),
        ]
        self.cookies.insert(data)

        # get cookies
        cookies = self.cookies.select(('domain1', 'domain2'))

        # check for same length
        self.assertEqual(3, len(cookies))

        # check for same data
        filtered_data = [c for c in data if c[2] == 'domain1' or c[2] == 'domain2']
        for c in cookies:
            self.assertIn(tuple(c.values()), filtered_data)

    def test_insert_tuple(self):
        # prepare data
        data = ('name', 'value', 'domain1', 'path1', int(time.time()))
        self.cookies.insert([data])

        # get all the data from database
        rows = self._get_rows()

        # tests
        self.assertEqual(1, len(rows))
        self.assertEqual(data, rows[0])

    def test_insert_cookiejar(self):
        # prepare data
        data = ('name', 'value', 'domain1', 'path1', int(time.time()))
        cj = RequestsCookieJar()
        cj.set('name', 'value', domain='domain1', path='path1', expires=int(time.time()))
        self.cookies.insert(cj)

        # get all the data from database
        rows = self._get_rows()

        # tests
        self.assertEqual(1, len(rows))
        self.assertEqual(data, rows[0])

    def test_insert_duplicate(self):
        # prepare data
        data = ('name', 'value', 'domain1', 'path1', int(time.time()))

        # test duplicate error
        with self.assertRaises(DuplicateCookieError):
            self.cookies.insert([data, data])

        # get all the data from database
        rows = self._get_rows()

        # test no data was added
        self.assertEqual(0, len(rows))

    def test_delete_no_domain(self):
        # empty list
        with self.assertRaises(ValueError):
            self.cookies.delete([])

        # None
        with self.assertRaises(ValueError):
            self.cookies.delete(None)

    def test_delete_one(self):
        # prepare data
        self.cookies.insert([
            ('name', 'value', 'domain1', 'path1', int(time.time())),
            ('name', 'value', 'domain2', 'path1', int(time.time())),
            ('name2', 'value', 'domain2', 'path1', int(time.time())),
            ('name2', 'value', 'domain3', 'path1', int(time.time())),
        ])

        # check successfull insertion
        rows = self._get_rows()
        self.assertEqual(4, len(rows))

        # check deletion
        self.cookies.delete('domain1')
        rows = self._get_rows()
        self.assertEqual(3, len(rows))

    def test_delete_many(self):
        self.cookies.insert([
            ('name', 'value', 'domain1', 'path1', int(time.time())),
            ('name', 'value', 'domain2', 'path1', int(time.time())),
            ('name2', 'value', 'domain1', 'path1', int(time.time())),
            ('name2', 'value', 'domain2', 'path1', int(time.time())),
            ('name2', 'value', 'domain3', 'path1', int(time.time())),
        ])

        # check successful insertion
        rows = self._get_rows()
        self.assertEqual(5, len(rows))

        # check deletion
        self.cookies.delete(('domain1', 'domain2'))
        rows = self._get_rows()
        self.assertEqual(1, len(rows))

    def test_all(self):
        data = [
            ('name', 'value', 'domain1', 'path1', int(time.time())),
            ('name', 'value', 'domain2', 'path1', int(time.time())),
            ('name4', 'value', 'domain3', 'path1', int(time.time())),
        ]
        self.cookies.insert(data)

        rows = self.cookies.all()

        # check cookies amount
        self.assertEqual(len(data), len(rows))

        # check data
        try:
            for cookie in rows:
                data.remove(tuple(cookie.values()))
        except ValueError:
            self.fail('not matching cookie found in rows unexpectedly')

        # check all data removed
        self.assertEqual(0, len(data))

    def test_check_expired_false(self):
        now = int(datetime.now().timestamp())
        now += 24 * 60 * 60  # go forward a days
        self.cookies.insert([
            ('name', 'value', 'domain1', 'path1', now),
            ('name', 'value', 'domain2', 'path1', now),
        ])

        cookies = self.cookies.all()

        self.assertFalse(self.cookies.check_expired(cookies))

    def test_check_expired_true(self):
        now = int(datetime.now().timestamp())
        now -= 2 * 24 * 60 * 60  # go back two days
        self.cookies.insert([
            ('name', 'value', 'domain1', 'path1', now),
            ('name', 'value', 'domain2', 'path1', now),
        ])

        cookies = self.cookies.all()

        self.assertTrue(self.cookies.check_expired(cookies))

    def tearDown(self) -> None:
        self.cookies.close()

    def _get_rows(self):
        with self.cookies.conn:
            self.cookies.cursor.execute("SELECT * FROM cookies")
        return self.cookies.cursor.fetchall()
