from functools import lru_cache
from typing import Optional

from novelsave_sources.exceptions import UnknownSourceException
from novelsave_sources.utils import parse_source

from .source_gateway import SourceGateway
from ...core.services.source import BaseSourceGatewayProvider
from ...utils.adapters import SourceAdapter


class SourceGatewayProvider(BaseSourceGatewayProvider):
    def __init__(self, source_adapter: SourceAdapter):
        self.source_adapter = source_adapter

    @lru_cache(1)
    def source_from_url(self, url: str) -> Optional[SourceGateway]:
        """gives source service from url provided"""
        try:
            return SourceGateway(parse_source(url), source_adapter=self.source_adapter)
        except UnknownSourceException:
            # TODO prefer throwing exceptions instead of returning [None]
            return None
