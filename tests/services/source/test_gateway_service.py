from unittest.mock import Mock

import pytest

from novelsave.exceptions import CookieBrowserNotSupportedException
from novelsave.services.source import SourceGateway


@pytest.fixture
def source_gateway():
    return SourceGateway(Mock(), Mock())


def test_use_cookies_from_browser_attribute_error(mocker, source_gateway):
    mocker.patch(
        "novelsave.services.source.source_gateway.browser_cookie3.chrome",
        side_effect=AttributeError(),
    )

    with pytest.raises(CookieBrowserNotSupportedException):
        source_gateway.use_cookies_from_browser("chrome")
