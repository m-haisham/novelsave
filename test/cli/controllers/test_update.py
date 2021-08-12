import unittest
from unittest.mock import patch

from loguru import logger

from novelsave.cli.controllers import update


class TestUpdateController(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()

    @patch('novelsave.cli.controllers._update.create_novel', return_value=None)
    @patch('novelsave.cli.controllers._update.get_novel', return_value=None)
    def test_update_not_exists(self, get_novel, create_novel):
        with self.assertRaises(SystemExit):
            update('not int', False)
        get_novel.assert_called_with('not int')
        create_novel.assert_not_called()

        with self.assertRaises(SystemExit):
            update('1', False)
        get_novel.assert_called_with('1')
        create_novel.assert_not_called()

        update('https://my.site.org', False)
        get_novel.assert_called_with('https://my.site.org')
        create_novel.assert_called_with('https://my.site.org')

    @patch('novelsave.cli.controllers._update.download_pending')
    @patch('novelsave.cli.controllers._update.update_novel')
    @patch('novelsave.cli.controllers._update.get_novel', return_value='novel')
    def test_update_exists(self, get_novel, update_novel, download_pending):
        url = 'https://novel.site'
        update(url, False)

        get_novel.assert_called_with(url)
        update_novel.assert_called_with('novel')
        download_pending.assert_called_with('novel')

    @patch('novelsave.cli.controllers._update.download_pending')
    @patch('novelsave.cli.controllers._update.update_novel')
    @patch('novelsave.cli.controllers._update.get_novel', return_value='novel')
    def test_update_exists_skip_chapters(self, get_novel, update_novel, download_pending):
        url = 'https://novel.site'
        update(url, skip_chapters=True)

        get_novel.assert_called_with(url)
        update_novel.assert_called_with('novel')
        download_pending.assert_not_called()

