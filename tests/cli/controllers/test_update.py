from unittest.mock import DEFAULT, Mock

import pytest

from novelsave.cli.controllers import update
from novelsave.cli.controllers._update import helpers


@pytest.fixture
def mock_helpers(mocker):
    def wrapped():
        mocker.patch.multiple(
            helpers,
            download_assets=DEFAULT,
            download_chapters=DEFAULT,
            download_thumbnail=DEFAULT,
            update_novel=DEFAULT,
            create_novel=DEFAULT,
            get_novel=DEFAULT,
        )

    return wrapped


def test_update_not_exists(mocker, mock_helpers):
    mock_helpers()
    mocker.patch.object(helpers, "get_novel", side_effect=ValueError())
    mocker.patch.object(helpers, "create_novel", return_value=Mock())

    get_novel_spy = mocker.spy(helpers, "get_novel")
    create_novel_spy = mocker.spy(helpers, "create_novel")

    with pytest.raises(SystemExit):
        update("not int", 0, None, None)

    get_novel_spy.assert_called_with("not int")
    create_novel_spy.assert_not_called()

    with pytest.raises(SystemExit):
        update("1", 0, None, None)
    get_novel_spy.assert_called_with("1")
    create_novel_spy.assert_not_called()

    update("https://my.site.org", None, 0, None)
    get_novel_spy.assert_called_with("https://my.site.org")
    create_novel_spy.assert_called_with("https://my.site.org", None)


def test_update_exists(mocker, mock_helpers):
    mock_helpers()

    novel = Mock()
    mocker.patch.object(helpers, "get_novel", return_value=novel)

    get_novel_spy = mocker.spy(helpers, "get_novel")
    update_novel_spy = mocker.spy(helpers, "update_novel")
    download_chapters_spy = mocker.spy(helpers, "download_chapters")

    url = "https://novel.site"
    update(url, None, 1, None)

    get_novel_spy.assert_called_with(url)
    update_novel_spy.assert_called_with(novel, None)
    download_chapters_spy.assert_called_with(novel, 1, None)


def test_update_exists_skip_chapters(mocker, mock_helpers):
    mock_helpers()

    novel = Mock()
    mocker.patch.object(helpers, "get_novel", return_value=novel)

    get_novel_spy = mocker.spy(helpers, "get_novel")
    update_novel_spy = mocker.spy(helpers, "update_novel")
    download_chapters_spy = mocker.spy(helpers, "download_chapters")

    url = "https://novel.site"
    update(url, None, limit=0, threads=None)

    get_novel_spy.assert_called_with(url)
    update_novel_spy.assert_called_with(novel, None)
    download_chapters_spy.assert_not_called()
