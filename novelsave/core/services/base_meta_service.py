from abc import ABC, abstractmethod


class BaseMetaService(ABC):

    @property
    @abstractmethod
    def current_version(self) -> str:
        """Current application version"""

    @abstractmethod
    def get_latest_version(self) -> str:
        """Latest stable version of novelsave available for download"""
