import unittest
from pathlib import Path
from unittest.mock import patch

from novelsave.core.entities.novel import Novel
from novelsave.exceptions import SourceNotFoundException
from novelsave.services import PathService


@patch('novelsave.core.services.BaseNovelService')
@patch('novelsave.core.services.source.BaseSourceService')
class TestPathService(unittest.TestCase):
    data_dir = Path('~/data')
    save_dir = Path('~/test_novels')
    division_rules = {'.html': 'web'}

    def test_divide(self, source_service, novel_service):
        path_service = PathService(self.data_dir, self.save_dir, self.division_rules, novel_service, source_service)

        # when there is a specified directory
        r_path = Path('subdivide_test_dir/test_file.html')
        s_path = path_service.divide(r_path)
        self.assertEqual(Path(r_path).parent / 'web' / 'test_file.html', s_path)

        # when there is no specified directory
        r_path = Path('subdivide_test_dir/test_file.json')
        s_path = path_service.divide(r_path)
        self.assertEqual(Path(r_path), s_path)

    def test_get_novel_path_no_source(self, source_service, novel_service):
        source_service.source_from_url.side_effect = SourceNotFoundException('')

        path_service = PathService(self.data_dir, self.save_dir, self.division_rules, novel_service, source_service)
        path = path_service.novel_save_path(Novel(title='novel'))

        self.assertEqual(self.save_dir / 'novel', path)

    @patch('novelsave.core.services.source.BaseSourceGateway')
    def test_get_novel_path_with_source(self, source_service, novel_service, source_gateway):
        source_service.source_from_url.return_value = source_gateway
        source_gateway.name.return_value = 'source'

        path_service = PathService(self.data_dir, self.save_dir, self.division_rules, novel_service, source_service)
        path = path_service.novel_save_path(Novel(title='novel'))

        self.assertEqual(self.save_dir / 'source' / 'novel', path)

    def test_get_thumbnail_path(self, source_service, novel_service):
        novel = Novel(id=1, thumbnail_url='https://my.site/local%20assets/image.jpg')

        path_service = PathService(self.data_dir, self.save_dir, self.division_rules, novel_service, source_service)
        path = path_service.thumbnail_path(novel)

        self.assertEqual(self.data_dir / '1' / 'cover.jpg', path)

    def test_get_thumbnail_path_no_suffix(self, source_service, novel_service):
        novel = Novel(id=1, thumbnail_url='https://my.site/local%20assets/image')

        path_service = PathService(self.data_dir, self.save_dir, self.division_rules, novel_service, source_service)
        path = path_service.thumbnail_path(novel)

        self.assertEqual(self.data_dir / '1' / 'cover', path)

    def test_resolve_data_path(self, source_service, novel_service):
        path_service = PathService(self.data_dir, self.save_dir, self.division_rules, novel_service, source_service)

        test_paths = {
            Path('1/cover.jpg'): self.data_dir / Path('1/cover.jpg'),
            Path('../1/cover.jpg'): self.data_dir / Path('1/cover.jpg'),
            Path('./1/cover.jpg'): self.data_dir / Path('1/cover.jpg'),
        }

        for test_path, expected in test_paths.items():
            path = path_service.resolve_data_path(test_path)
            self.assertEqual(expected, path)

    def test_relative_to_data_dir(self, source_service, novel_service):
        test_path = self.data_dir / Path('file')

        path_service = PathService(self.data_dir, self.save_dir, self.division_rules, novel_service, source_service)
        path = path_service.relative_to_data_dir(test_path)

        self.assertEqual(Path('file'), path)
