from functools import lru_cache

from novelsave_sources.exceptions import UnknownSourceException
from novelsave_sources.utils import parse_source, parse_metasource

from .meta_source_gateway import MetaSourceGateway
from .source_gateway import SourceGateway
from ...core.services.source import BaseSourceGatewayProvider
from ...exceptions import NovelSourceNotFoundException, MetaDataSourceNotFoundException
from ...utils.adapters import SourceAdapter


class SourceGatewayProvider(BaseSourceGatewayProvider):
    def __init__(self, source_adapter: SourceAdapter):
        self.source_adapter = source_adapter

    @lru_cache(1)
    def source_from_url(self, url: str) -> SourceGateway:
        try:
            return SourceGateway(parse_source(url), source_adapter=self.source_adapter)
        except UnknownSourceException:
            raise NovelSourceNotFoundException(url)

    @lru_cache(1)
    def meta_source_from_url(self, url: str) -> MetaSourceGateway:
        try:
            return MetaSourceGateway(parse_metasource(url), source_adapter=self.source_adapter)
        except UnknownSourceException:
            raise MetaDataSourceNotFoundException(url)
