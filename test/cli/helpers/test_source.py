import unittest
from unittest.mock import MagicMock, patch

from loguru import logger

from novelsave.cli.helpers.source import get_source_gateway


class TestSourceHelper(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()

    @patch('novelsave.services.source.SourceGatewayProvider')
    def test_get_source_gateway_none(self, source_gateway_provider):
        source_gateway_provider.source_from_url.return_value = None

        with self.assertRaises(SystemExit):
            get_source_gateway('https://not.a.provider.site', source_gateway_provider)

    @patch('novelsave.services.source.SourceGateway')
    @patch('novelsave.services.source.SourceGatewayProvider')
    def test_get_source_gateway(self, source_gateway_provider, source_gateway):
        source_gateway_provider.source_from_url.return_value = source_gateway

        result = get_source_gateway('https://not.a.provider.site', source_gateway_provider)
        self.assertEqual(source_gateway_provider.source_from_url.return_value, result)

