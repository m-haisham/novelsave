import unittest
from unittest.mock import patch, MagicMock

from novelsave.cli.controllers.novel import create_novel
from novelsave.services import NovelService
from novelsave.services.source import SourceGateway, SourceGatewayProvider


class TestNovelController(unittest.TestCase):

    def test_create_novel(self):
        pass
