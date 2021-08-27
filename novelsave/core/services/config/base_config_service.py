from abc import ABC, abstractmethod


class BaseConfigService(ABC):

    @abstractmethod
    def get_novel_dir(self):
        """get novels save directory"""

    @abstractmethod
    def set_novel_dir(self, path):
        """set novels save directory"""

    @abstractmethod
    def reset_novel_dir(self):
        """reset novels save directory"""
