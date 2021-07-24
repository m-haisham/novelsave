import unittest

from novelsave.services.novel_service import NovelService


class TestNovelService(unittest.TestCase):

    novel_service = NovelService()

    def test_get_novel_by_url(self):
        pass
