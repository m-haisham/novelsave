import unittest

from novelsave.utils.helpers.pattern import url_pattern, int_pattern

class TestPattern(unittest.TestCase):
    def test_url_pattern_match(self):
        self.assertIsNotNone(url_pattern.match('https://website.com/'))
        self.assertIsNone(url_pattern.match('com.website.com/'))
        self.assertIsNotNone(url_pattern.match('https://www.website.net/'))
        self.assertIsNotNone(url_pattern.match('https://ww1.website.com'))
        self.assertIsNotNone(url_pattern.match('http://website.com/'))
        self.assertIsNotNone(url_pattern.match('http://website.com/hello'))
        self.assertIsNone(url_pattern.match('htt://website.net'))

    def test_int_pattern_match(self):
        self.assertIsNotNone(int_pattern.match('12 ads'))
        self.assertIsNone(int_pattern.match('ads'))