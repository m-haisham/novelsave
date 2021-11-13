import pytest

from novelsave.utils.helpers import url_helper


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/mHaisham/novelsave/",
        "https://www.webnovel.com/book/lord-of-mysteries_11022733006234505",
        "https://www.scribblehub.com/series/10700/tree-of-aeons-an-isekai-story/"
        "https://www.royalroad.com/fiction/21410/super-minion",
    ],
)
def test_is_url_true(url):
    assert url_helper.is_url(
        url
    ), "Was not identified as a url, even though its is valid"


@pytest.mark.parametrize(
    "url",
    [
        "https:/github.com",
        "this",
        "1",
        "1.001",
        "https://1",
    ],
)
def test_is_url_false(url):
    assert not url_helper.is_url(
        url
    ), "Was identified as url, even thought it isn't valid"
