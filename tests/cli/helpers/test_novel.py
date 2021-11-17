from unittest.mock import MagicMock, patch

import pytest

from novelsave.client.cli.helpers import novel as novel_helper
from novelsave.exceptions import CookieBrowserNotSupportedException


def test_set_cookies(mocker):
    source_gateway = mocker.patch("novelsave.cli.helpers.novel.BaseSourceGateway")
    source_gateway.use_cookies_from_browser.side_effect = (
        CookieBrowserNotSupportedException("")
    )
    novel_helper.set_cookies(source_gateway, None)
    source_gateway.use_cookies_from_browser.assert_not_called()

    source_gateway = mocker.patch("novelsave.cli.helpers.novel.BaseSourceGateway")
    source_gateway.use_cookies_from_browser.side_effect = (
        CookieBrowserNotSupportedException("chrome")
    )
    with pytest.raises(SystemExit):
        novel_helper.set_cookies(source_gateway, "chrome")
    source_gateway.use_cookies_from_browser.assert_called_with("chrome")

    source_gateway = mocker.patch("novelsave.cli.helpers.novel.BaseSourceGateway")
    novel_helper.set_cookies(source_gateway, "chrome")


def test_get_novel_url(mocker):
    novel_service = mocker.patch("novelsave.services.NovelService")
    novel_service.get_novel_by_url.return_value = None
    with pytest.raises(ValueError):
        novel_helper.get_novel("https://test.site", False, novel_service)
    novel_service.get_novel_by_url.assert_called_with("https://test.site")

    novel = MagicMock()
    novel_service.get_novel_by_url.return_value = novel
    result = novel_helper.get_novel("https://test.com", False, novel_service)
    novel_service.get_novel_by_url.assert_called_with("https://test.com")
    assert novel == result


def test_get_novel_id(mocker):
    novel_service = mocker.patch("novelsave.services.NovelService")
    novel_service.get_novel_by_id.return_value = None
    with pytest.raises(ValueError):
        novel_helper.get_novel("1", False, novel_service)
    novel_service.get_novel_by_id.assert_called_with(1)

    novel = MagicMock()
    novel_service.get_novel_by_id.return_value = novel
    result = novel_helper.get_novel("2", False, novel_service)
    novel_service.get_novel_by_id.assert_called_with(2)
    assert novel == result


@patch("novelsave.services.NovelService")
def test_get_novel_no_int_id(novel_service):
    with pytest.raises(SystemExit):
        novel_helper.get_novel("h", False, novel_service)


def test_get_or_create_no_novel(mocker):
    mocker.patch("novelsave.cli.helpers.novel.get_novel", return_value=None)
    mocker.patch("novelsave.cli.helpers.novel.create_novel", return_value="novel")

    result = novel_helper.get_or_create_novel("https://test.site")
    assert "novel" == result

    with pytest.raises(SystemExit):
        novel_helper.get_or_create_novel("1")

    with pytest.raises(SystemExit):
        novel_helper.get_or_create_novel("something")


def test_get_or_create_no_novel_ok(mocker):
    mocker.patch("novelsave.cli.helpers.novel.get_novel", return_value="novel")
    mocker.patch("novelsave.cli.helpers.novel.create_novel", return_value="novel")

    result = novel_helper.get_or_create_novel("https://test.site")
    assert "novel" == result

    result = novel_helper.get_or_create_novel("1")
    assert "novel" == result
