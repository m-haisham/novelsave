import unittest

from novelsave.sources.crawler import Crawler


class TestCrawler(unittest.TestCase):
    crawler = Crawler()

    def test_parse_query(self):
        test_data = {
            'p=117': {
                'p': ['117'],
            },
            'a=1&a=2&b=4&a=3': {
                'a': ['1', '2', '3'],
                'b': ['4'],
            },
            'a=1&a=1&a=2': {
                'a': ['1', '2'],
            },
            'a=1,2,3&b=4': {
                'a': ['1', '2', '3'],
                'b': ['4'],
            },
        }

        for query, expected in test_data.items():
            actual = self.crawler.parse_query(query)
            self.assertListEqual(sorted(list(actual.keys())), sorted(list(expected.keys())))

            for key in actual.keys():
                self.assertListEqual(sorted(actual[key]), sorted(expected[key]))
