from typing import List

from novelsave_sources.sources.metadata.metasource import MetaSource

from novelsave.core.dtos import MetaDataDTO
from novelsave.core.services.source import BaseMetaSourceGateway
from novelsave.utils.adapters import SourceAdapter


class MetaSourceGateway(BaseMetaSourceGateway):

    def __init__(self, meta_source: MetaSource, source_adapter: SourceAdapter):
        self.meta_source = meta_source
        self.source_adapter = source_adapter

    @property
    def name(self):
        return type(self.meta_source).__name__

    def metadata_by_url(self, url: str) -> List[MetaDataDTO]:
        metadata = self.meta_source.retrieve(url)

        return [
            self.source_adapter.metadata_to_internal(m)
            for m in metadata
        ]
