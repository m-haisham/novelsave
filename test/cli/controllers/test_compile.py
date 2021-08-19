import unittest
from unittest.mock import patch

from loguru import logger

from novelsave.cli.controllers import package


@patch('novelsave.services.packagers.PackagerProvider')
@patch('novelsave.cli.controllers._package.get_novel')
class TestCompileController(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()

    def test_compile_no_novel(self, get_novel, compiler_provider):
        get_novel.side_effect = ValueError()

        with self.assertRaises(SystemExit):
            package('https://novel.site', compiler_provider)

    def test_compile_with_novel(self, get_novel, compiler_provider):
        get_novel.return_value = 'novel'

        package('https://novel.site', compiler_provider)
