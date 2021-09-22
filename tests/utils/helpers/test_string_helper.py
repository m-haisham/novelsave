import unittest

import novelsave.utils.helpers.url_helper
from novelsave.utils.helpers import string_helper


class TestStringHelper(unittest.TestCase):

    def test_is_url_true(self):
        tests = [
            'https://github.com/mHaisham/novelsave/',
            'https://www.webnovel.com/book/lord-of-mysteries_11022733006234505',
            'https://www.scribblehub.com/series/10700/tree-of-aeons-an-isekai-story/'
            'https://www.royalroad.com/fiction/21410/super-minion',
        ]

        for url in tests:
            self.assertTrue(novelsave.utils.helpers.url_helper.is_url(url), msg=f"{url=} is not a url")

    def test_is_url_false(self):
        tests = [
            'https:/github.com',
            'this',
            '1',
            '1.001',
            'https://1',
        ]

        for url in tests:
            self.assertFalse(novelsave.utils.helpers.url_helper.is_url(url), msg=f"{url=} is a url")
