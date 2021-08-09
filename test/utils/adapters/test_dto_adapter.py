import unittest

from novelsave.core.dtos import NovelDTO
from novelsave.core.entities.novel import Novel, NovelUrl
from novelsave.utils.adapters import DTOAdapter


class TestDTOAdapter(unittest.TestCase):

    dto_adapter = DTOAdapter()

    def test_novel_from_dto(self):
        test_dto = NovelDTO(
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

        actual_novel, actual_url = self.dto_adapter.novel_from_dto(test_dto)
        for attrib in {'title', 'author', 'synopsis', 'thumbnail_url', 'lang'}:
            self.assertEqual(getattr(expected_novel, attrib), getattr(actual_novel, attrib))

        for attrib in {'url'}:
            self.assertEqual(getattr(expected_url, attrib), getattr(actual_url, attrib))
