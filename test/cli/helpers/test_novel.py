import unittest
from unittest.mock import MagicMock, patch

from loguru import logger

from novelsave.cli.helpers import novel as novel_helper


class TestNovelHelper(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()

    @patch('novelsave.services.source.SourceGatewayProvider')
    @patch('novelsave.services.NovelService')
    def test_create_novel_no_source(self, novel_service, source_gateway_provider):
        source_gateway_provider.source_from_url.return_value = None

        with self.assertRaises(SystemExit):
            novel_helper.create_novel('https://www.test.site', novel_service, source_gateway_provider)

        novel_service.insert_novel.assert_not_called()
        novel_service.insert_chapters.assert_not_called()
        novel_service.insert_metadata.assert_not_called()

    @patch('novelsave.services.source.SourceGatewayProvider')
    @patch('novelsave.services.source.SourceGateway')
    @patch('novelsave.services.NovelService')
    def test_create_novel_with_source(self, novel_service, source_gateway, source_gateway_provider):
        novel_service.insert_novel.return_value = 'novel_entity'
        source_gateway_provider.source_from_url.return_value = source_gateway
        source_gateway.novel_by_url.return_value = 'novel', ['chapters'], ['metadata']

        novel = novel_helper.create_novel('https://www.test.site', novel_service, source_gateway_provider)

        novel_service.insert_novel.assert_called_with('novel')
        novel_service.insert_chapters.assert_called_with(['chapters'])
        novel_service.insert_metadata.assert_called_with(['metadata'])

        self.assertEqual(novel_service.insert_novel.return_value, novel)

    @patch('novelsave.services.NovelService')
    def test_get_novel_url(self, novel_service):
        novel_service.get_novel_by_url.return_value = None
        result = novel_helper.get_novel('https://test.site', novel_service)
        novel_service.get_novel_by_url.assert_called_with('https://test.site')
        self.assertIsNone(result)

        novel = MagicMock()
        novel_service.get_novel_by_url.return_value = novel
        result = novel_helper.get_novel('https://test.com', novel_service)
        novel_service.get_novel_by_url.assert_called_with('https://test.com')
        self.assertEqual(novel, result)

    @patch('novelsave.services.NovelService')
    def test_get_novel_id(self, novel_service):
        novel_service.get_novel_by_id.return_value = None
        result = novel_helper.get_novel('1', novel_service)
        novel_service.get_novel_by_id.assert_called_with(1)
        self.assertIsNone(result)

        novel = MagicMock()
        novel_service.get_novel_by_id.return_value = novel
        result = novel_helper.get_novel('2', novel_service)
        novel_service.get_novel_by_id.assert_called_with(2)
        self.assertEqual(novel, result)

    @patch('novelsave.services.NovelService')
    def test_get_novel_no_int_id(self, novel_service):
        with self.assertRaises(SystemExit):
            novel_helper.get_novel('h', novel_service)

    @patch('novelsave.cli.helpers.novel.get_novel', return_value=None)
    @patch('novelsave.cli.helpers.novel.create_novel', return_value='novel')
    def test_get_or_create_no_novel(self, create_novel, get_novel):
        result = novel_helper.get_or_create_novel('https://test.site')
        self.assertEqual('novel', result)

        with self.assertRaises(SystemExit):
            novel_helper.get_or_create_novel('1')

        with self.assertRaises(SystemExit):
            novel_helper.get_or_create_novel('something')

    @patch('novelsave.cli.helpers.novel.get_novel', return_value='novel')
    @patch('novelsave.cli.helpers.novel.create_novel', return_value='novel')
    def test_get_or_create_no_novel(self, create_novel, get_novel):
        result = novel_helper.get_or_create_novel('https://test.site')
        self.assertEqual('novel', result)

        result = novel_helper.get_or_create_novel('1')
        self.assertEqual('novel', result)