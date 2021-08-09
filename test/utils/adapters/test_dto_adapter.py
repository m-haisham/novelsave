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

        actual_tuple = self.dto_adapter.novel_from_dto(test_dto)
        self.assertTupleEqual((expected_novel, expected_url), actual_tuple)