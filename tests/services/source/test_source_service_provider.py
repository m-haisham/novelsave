import unittest
from unittest.mock import Mock

from novelsave_sources.sources.novel import sources

from novelsave.exceptions import SourceNotFoundException
from novelsave.services.source import SourceService


class TestSourceServiceProvider(unittest.TestCase):
    source_service = SourceService(Mock())

    def test_source_from_url(self):
        source_service = self.source_service.source_from_url(sources[0].base_urls[0])
        self.assertIsNotNone(source_service)

    def test_source_from_url_unavailable(self):
        with self.assertRaises(SourceNotFoundException):
            self.source_service.source_from_url('https://test.site')
