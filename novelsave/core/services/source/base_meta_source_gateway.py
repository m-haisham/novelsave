from abc import ABC, abstractmethod
from typing import List

from novelsave.core.dtos import MetaDataDTO


class BaseMetaSourceGateway(ABC):

    @property
    @abstractmethod
    def name(self):
        """name of the corresponding metadata source"""

    @abstractmethod
    def metadata_by_url(self, url: str) -> List[MetaDataDTO]:
        """get metadata from the url"""
