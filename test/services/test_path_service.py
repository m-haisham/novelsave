import unittest
from pathlib import Path
from unittest.mock import patch

from novelsave.core.entities.novel import Novel
from novelsave.services import PathService


@patch('novelsave.core.services.BaseNovelService')
@patch('novelsave.core.services.source.BaseSourceGatewayProvider')
class TestPathService(unittest.TestCase):
    data_dir = Path('~/data')
    save_dir = Path('~/test_novels')

    def test_get_novel_path_no_source(self, source_provider, novel_service):
        source_provider.source_from_url.return_value = None

        save_service = PathService(self.data_dir, self.save_dir, novel_service, source_provider)
        path = save_service.get_novel_path(Novel(title='novel'))

        self.assertEqual(self.save_dir / 'novel', path)

    @patch('novelsave.core.services.source.BaseSourceGateway')
    def test_get_novel_path_with_source(self, source_provider, novel_service, source_gateway):
        source_provider.source_from_url.return_value = source_gateway
        source_gateway.source_name.return_value = 'source'

        save_service = PathService(self.data_dir, self.save_dir, novel_service, source_provider)
        path = save_service.get_novel_path(Novel(title='novel'))

        self.assertEqual(self.save_dir / 'source' / 'novel', path)

    def test_get_thumbnail_path(self, source_provider, novel_service):
        novel = Novel(id=1, thumbnail_url='https://my.site/local%20assets/image.jpg')

        path_service = PathService(self.data_dir, self.save_dir, novel_service, source_provider)
        path = path_service.get_thumbnail_path(novel)

        self.assertEqual(self.data_dir / '1' / 'cover.jpg', path)

    def test_get_thumbnail_path_no_suffix(self, source_provider, novel_service):
        novel = Novel(id=1, thumbnail_url='https://my.site/local%20assets/image')

        path_service = PathService(self.data_dir, self.save_dir, novel_service, source_provider)
        path = path_service.get_thumbnail_path(novel)

        self.assertEqual(self.data_dir / '1' / 'cover.jpg', path)

    def test_resolve_data_path(self, source_provider, novel_service):
        path_service = PathService(self.data_dir, self.save_dir, novel_service, source_provider)

        test_paths = {
            Path('1/cover.jpg'): self.data_dir / Path('1/cover.jpg'),
            Path('../1/cover.jpg'): self.data_dir / Path('1/cover.jpg'),
            Path('./1/cover.jpg'): self.data_dir / Path('1/cover.jpg'),
        }

        for test_path, expected in test_paths.items():
            path = path_service.resolve_data_path(test_path)
            self.assertEqual(expected, path)

    def test_relative_to_data_dir(self, source_provider, novel_service):
        test_path = self.data_dir / Path('file')

        path_service = PathService(self.data_dir, self.save_dir, novel_service, source_provider)
        path = path_service.relative_to_data_dir(test_path)

        self.assertEqual(Path('file'), path)