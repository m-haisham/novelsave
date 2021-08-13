import unittest
from unittest.mock import patch

from loguru import logger

from novelsave.cli.controllers import compile


class TestCompileController(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()

    @patch('novelsave.services.compilers.CompilerProvider')
    @patch('novelsave.cli.controllers._compile.get_novel', return_value=None)
    def test_compile_no_novel(self, get_novel, compiler_provider):
        with self.assertRaises(SystemExit):
            compile('https://novel.site', compiler_provider)

    @patch('novelsave.services.compilers.CompilerProvider')
    @patch('novelsave.cli.controllers._compile.get_novel', return_value='novel')
    def test_compile_with_novel(self, get_novel, compiler_provider):
        compile('https://novel.site', compiler_provider)
