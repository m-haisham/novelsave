import unittest
from pathlib import Path
from unittest.mock import patch

from novelsave.core.entities.novel import Novel
from novelsave.services import SaveService


@patch('novelsave.core.services.BaseNovelService')
@patch('novelsave.core.services.source.BaseSourceGatewayProvider')
class TestSaveService(unittest.TestCase):

    save_dir = Path('~/test_novels')

    def test_get_novel_path_no_source(self, source_provider, novel_service):
        source_provider.source_from_url.return_value = None

        save_service = SaveService(self.save_dir, novel_service, source_provider)
        path = save_service.get_novel_path(Novel(title='novel'))

        self.assertEqual(self.save_dir / 'novel', path)

    @patch('novelsave.core.services.source.BaseSourceGateway')
    def test_get_novel_path_with_source(self, source_provider, novel_service, source_gateway):
        source_provider.source_from_url.return_value = source_gateway
        source_gateway.source_name.return_value = 'source'

        save_service = SaveService(self.save_dir, novel_service, source_provider)
        path = save_service.get_novel_path(Novel(title='novel'))

        self.assertEqual(self.save_dir / 'source' / 'novel', path)
