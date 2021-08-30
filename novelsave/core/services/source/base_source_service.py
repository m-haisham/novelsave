from abc import ABC, abstractmethod

from . import BaseSourceGateway, BaseMetaSourceGateway


class BaseSourceService(ABC):

    @property
    @abstractmethod
    def current_version(self) -> str:
        """installed current_version of sources"""

    @abstractmethod
    def get_latest_version(self) -> str:
        """Latest stable version available for download"""

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
