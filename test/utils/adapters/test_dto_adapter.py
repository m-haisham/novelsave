import unittest

from novelsave.core.dtos import NovelDTO, ChapterDTO, MetaDataDTO
from novelsave.core.entities.novel import Novel, NovelUrl, Chapter, MetaData, Volume
from novelsave.utils.adapters import DTOAdapter


class TestDTOAdapter(unittest.TestCase):

    dto_adapter = DTOAdapter()

    def test_novel_from_dto(self):
        novel_dto = NovelDTO(
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

        expected_novel = Novel(
            title="title",
            author="author",
            synopsis="a nice description",
            thumbnail_url='thumbnail',
            lang='language',
        )

        expected_url = NovelUrl(
            url='link',
        )

        actual_novel, actual_url = self.dto_adapter.novel_from_dto(novel_dto)
        for attrib in {'title', 'author', 'synopsis', 'thumbnail_url', 'lang'}:
            self.assertEqual(getattr(expected_novel, attrib), getattr(actual_novel, attrib))

        for attrib in {'url'}:
            self.assertEqual(getattr(expected_url, attrib), getattr(actual_url, attrib))

    def test_update_novel_from_dto(self):
        novel_dto = NovelDTO(
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

        expected_novel = Novel(
            title="title",
            author="author",
            synopsis="a nice description",
            thumbnail_url='thumbnail',
            lang='language',
        )

        actual_novel = self.dto_adapter.update_novel_from_dto(Novel(), novel_dto)
        for attrib in {'title', 'author', 'synopsis', 'thumbnail_url', 'lang'}:
            self.assertEqual(getattr(expected_novel, attrib), getattr(actual_novel, attrib))

    def test_volume_from_chapter_dtos(self):
        novel = Novel(id=2)

        chapter_dtos = [
            ChapterDTO(index=-1, title='', url='', volume=(1, 'volume')),
            ChapterDTO(index=-1, title='', url='', volume=(1, 'volume')),
            ChapterDTO(index=-1, title='', url='', volume=(1, 'volume')),
            ChapterDTO(index=-1, title='', url='', volume=(2, 'volume 2')),
            ChapterDTO(index=-1, title='', url='', volume=None),
            ChapterDTO(index=1, title='', url='', volume=None),
            ChapterDTO(index=-1, title='', url='', volume=(3,)),
        ]

        expected_volumes = {
            Volume(index=1, name='volume', novel_id=novel.id): chapter_dtos[:3],
            Volume(index=2, name='volume 2', novel_id=novel.id): chapter_dtos[3:4],
            Volume(index=-1, name='_default', novel_id=novel.id): chapter_dtos[4:6],
        }

        actual_volumes = self.dto_adapter.volumes_from_chapter_dtos(novel, chapter_dtos)
        self.assertEqual(len(expected_volumes), len(actual_volumes))
        for (expected_volume, expected_chapter_dtos), (actual_volume, actual_chapter_dtos) in \
                zip(expected_volumes.items(), actual_volumes.items()):
            self.assertListEqual(expected_chapter_dtos, actual_chapter_dtos)
            for attrib in {'id', 'index', 'name', 'novel_id'}:
                self.assertEqual(getattr(expected_volume, attrib), getattr(actual_volume, attrib))

    def test_chapter_from_dto(self):
        volume = Volume(id=1)

        chapter_dto = ChapterDTO(
            index=1,
            title='chapter title',
            url='https://my.chapter.org',
            content='content',
            volume=(1, 'volume'),
        )

        expected_chapter = Chapter(
            id=None,
            index=1,
            title='chapter title',
            url='https://my.chapter.org',
            volume_id=volume.id,
        )

        actual_chapter = self.dto_adapter.chapter_from_dto(volume, chapter_dto)
        for attrib in {'id', 'index', 'title', 'url', 'volume_id'}:
            self.assertEqual(getattr(expected_chapter, attrib), getattr(actual_chapter, attrib))

    def test_chapter_to_dto(self):
        test_chapter = Chapter(
            index=1,
            title="something",
            url="url",
        )

        expected_dto = ChapterDTO(
            index=1,
            title='something',
            url='url',
        )

        actual_dto = self.dto_adapter.chapter_to_dto(test_chapter)
        self.assertEqual(expected_dto, actual_dto)

    def test_metadata_from_dto(self):
        novel = Novel(id=1)

        metadata_dto = MetaDataDTO(
            name='name',
            value='value',
            namespace='ns',
            others={'role': 'this'},
        )

        expected_metadata = MetaData(
            name='name',
            value='value',
            namespace='ns',
            others='{"role": "this"}',
            novel_id=novel.id,
        )

        actual_metadata = self.dto_adapter.metadata_from_dto(novel, metadata_dto)
        for attrib in {'name', 'value', 'namespace', 'others', 'novel_id'}:
            self.assertEqual(getattr(expected_metadata, attrib), getattr(actual_metadata, attrib))