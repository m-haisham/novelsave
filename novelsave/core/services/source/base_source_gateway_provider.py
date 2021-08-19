from abc import ABC, abstractmethod
from typing import Optional

from . import BaseSourceGateway, BaseMetaSourceGateway


class BaseSourceGatewayProvider(ABC):

    @abstractmethod
    def source_from_url(self, url: str) -> BaseSourceGateway:
        """find source gateway pointing towards source that handles the url specified

        :raises NovelSourceNotFoundException: if no source if available for the url
        """

    @abstractmethod
    def meta_source_from_url(self, url: str) -> BaseMetaSourceGateway:
        """find metadata source gateway pointing towards source that's handles the url specified

        :raises MetaDataSourceNotFoundException: if no source if available for the url
        """
