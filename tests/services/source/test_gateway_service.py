from http.cookiejar import CookieJar, Cookie
import unittest
from http.cookies import SimpleCookie
from unittest.mock import patch, MagicMock

from novelsave.exceptions import CookieBrowserNotSupportedException
from novelsave.services.source import SourceGateway


@patch('novelsave.services.source.source_gateway.SourceAdapter')
@patch('novelsave.services.source.source_gateway.Source')
class TestSourceService(unittest.TestCase):

    def test_use_cookies_from_browser_attribute_error(self, source, source_adapter):
        source_gateway = SourceGateway(source, source_adapter)

        with patch(
                'novelsave.services.source.source_gateway.browser_cookie3.chrome',
                side_effect=AttributeError(),
        ):
            with self.assertRaises(CookieBrowserNotSupportedException):
                source_gateway.use_cookies_from_browser('chrome')