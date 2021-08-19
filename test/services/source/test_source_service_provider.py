import unittest
from unittest.mock import Mock

from novelsave_sources.sources.novel import sources

from novelsave.exceptions import NovelSourceNotFoundException
from novelsave.services.source import SourceGatewayProvider


class TestSourceServiceProvider(unittest.TestCase):
    source_provider = SourceGatewayProvider(Mock())

    def test_source_from_url(self):
        source_service = self.source_provider.source_from_url(sources[0].base_urls[0])
        self.assertIsNotNone(source_service)

    def test_source_from_url_unavailable(self):
        with self.assertRaises(NovelSourceNotFoundException):
            self.source_provider.source_from_url('https://test.site')
