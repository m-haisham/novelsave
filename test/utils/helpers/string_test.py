import unittest

from novelsave.utils.helpers import StringHelper


class TestStringHelper(unittest.TestCase):
    def test_collect_integers(self):
        s1 = '1, (4) => 4 -1 = 3 / 2 = 1.5'
        r1 = (1, 4, 4, 1, 3, 2, 1, 5)
        integers = StringHelper.collect_integers(s1)

        self.assertTupleEqual(r1, integers)

    def test_clean(self):
        s1 = ' \\ /   ?'
        r1 = ' \\ /   ?'
        result = StringHelper.clean(s1)

        self.assertEqual(r1, result)

    def test_from_float(self):
        self.assertEqual('1.5', StringHelper.from_float(1.5))
        self.assertEqual('1.5', StringHelper.from_float(1.50))
        self.assertEqual('1.05', StringHelper.from_float(1.05))
        self.assertEqual('1.5', StringHelper.from_float(01.5))
        self.assertEqual('10.05', StringHelper.from_float(10.050000))
