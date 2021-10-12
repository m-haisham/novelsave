from abc import ABC, abstractmethod
from typing import Dict


class BaseConfigService(ABC):

    @abstractmethod
    def get_all_configs(self) -> Dict:
        """Get all configurations saved or default"""

    @abstractmethod
    def set_config(self, key: str, value: object):
        """Set configuration value of the specified key"""

    @abstractmethod
    def get_config(self, key: str) -> object:
        """Get saved configuration value otherwise return the default"""

    @abstractmethod
    def reset_config(self, key: str):
        """Reset the configuration value of the specified key"""
