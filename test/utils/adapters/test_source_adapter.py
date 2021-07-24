import unittest
from datetime import datetime

from novelsave_sources import models as source_models
from novelsave import view_models
from novelsave.utils.adapters import SourceAdapter


class TestSourceAdapter(unittest.TestCase):

    source_adapter = SourceAdapter()

    def test_novel_from_source_to_view(self):
        test_novel = source_models.Novel(
            title='title',
            author='author',
            synopsis='a nice description',
            thumbnail_url='thumbnail',
            lang='language',
            url='link',
        )

        expected_novel = view_models.Novel(
            id=None,
            title='title',
            author='author',
            synopsis='a nice description',
            thumbnail_url='thumbnail',
            thumbnail_path=None,
            lang='language',
            url='link',
            last_updated=None,
        )

        actual_novel = self.source_adapter.novel_from_source_to_view(test_novel)
        self.assertEqual(expected_novel, actual_novel)

    def test_novel_from_view_to_source(self):
        test_novel = view_models.Novel(
            id=1,
            title='title',
            author='author',
            synopsis='a nice description',
            thumbnail_url='thumbnail',
            thumbnail_path='source/novel/assets/image.png',
            lang='language',
            url='link',
            last_updated=datetime.now(),
        )

        expected_novel = source_models.Novel(
            title='title',
            author='author',
            synopsis='a nice description',
            thumbnail_url='thumbnail',
            lang='language',
            url='link',
        )

        actual_novel = self.source_adapter.novel_from_view_to_source(test_novel)
        self.assertEqual(expected_novel, actual_novel)
