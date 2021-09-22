import unittest
from datetime import datetime

from novelsave_sources import models as sm
from novelsave.core import dtos
from novelsave.utils.adapters import SourceAdapter


class TestSourceAdapter(unittest.TestCase):

    source_adapter = SourceAdapter()

    def test_novel_to_internal(self):
        test_novel = sm.Novel(
            title='title',
            author='author',
            synopsis='a nice description',
            thumbnail_url='thumbnail',
            lang='language',
            url='link',
        )

        expected_novel = dtos.NovelDTO(
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

        actual_novel = self.source_adapter.novel_to_internal(test_novel)
        self.assertEqual(expected_novel, actual_novel)

    def test_novel_from_internal(self):
        test_novel = dtos.NovelDTO(
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

        expected_novel = sm.Novel(
            title='title',
            author='author',
            synopsis='a nice description',
            thumbnail_url='thumbnail',
            lang='language',
            url='link',
        )

        actual_novel = self.source_adapter.novel_to_external(test_novel)
        self.assertEqual(expected_novel, actual_novel)

    def test_chapter_to_internal(self):
        test_chapter = sm.Chapter(
            index=1,
            no=20,
            title="title",
            paragraphs="paragraphs this is",
            volume=(1, "volume 1"),
            url="https://",
        )

        expected_chapter = dtos.ChapterDTO(
            index=1,
            title="title",
            content="paragraphs this is",
            volume=(1, "volume 1"),
            url="https://",
        )

        actual_chapter = self.source_adapter.chapter_to_internal(test_chapter)
        self.assertEqual(expected_chapter, actual_chapter)

    def test_chapter_from_internal(self):
        test_chapter = dtos.ChapterDTO(
            index=1,
            title="title",
            content="paragraphs this is",
            volume=(1, "volume 1"),
            url="https://",
        )

        expected_chapter = sm.Chapter(
            index=1,
            no=20,
            title="title",
            paragraphs="paragraphs this is",
            volume=(1, "volume 1"),
            url="https://",
        )

        actual_chapter = self.source_adapter.chapter_to_external(test_chapter)
        self.assertEqual(expected_chapter, actual_chapter)

    def test_chapter_content_to_internal(self):
        test_chapter = sm.Chapter(
            index=1,
            no=20,
            title="title",
            paragraphs="paragraphs this is",
            volume=(1, "volume 1"),
            url="https://",
        )

        expected_chapter = dtos.ChapterDTO(
            index=-1,
            title="",
            url="",
        )
        self.assertIsNone(expected_chapter.content)

        self.source_adapter.chapter_content_to_internal(test_chapter, expected_chapter)
        self.assertEqual(test_chapter.paragraphs, expected_chapter.content)

    def test_metadata_to_internal(self):
        test_metadata = sm.Metadata(
            name="name",
            value="value",
            others={"role": "something"},
            namespace="DC",
        )

        expected_metadata = dtos.MetaDataDTO(
            name="name",
            value="value",
            others={"role": "something"},
            namespace="DC",
        )

        actual_metadata = self.source_adapter.metadata_to_internal(test_metadata)
        self.assertEqual(expected_metadata, actual_metadata)

    def test_metadata_from_internal(self):
        test_metadata = dtos.MetaDataDTO(
            name="name",
            value="value",
            others={"role": "something"},
            namespace="DC",
        )

        expected_metadata = sm.Metadata(
            name="name",
            value="value",
            others={"role": "something"},
            namespace="DC",
        )

        actual_metadata = self.source_adapter.metadata_to_external(test_metadata)
        self.assertEqual(expected_metadata, actual_metadata)
