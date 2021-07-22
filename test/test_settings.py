import unittest

from novelsave import settings


class TestSettings(unittest.TestCase):

    def test_editable(self):
        """all editable configurations must have a default value in settings"""
        for value in settings.__editable__:
            self.assertIn(value, settings.__config__.keys())
