from abc import ABC, abstractmethod
from typing import Optional

from . import BaseSourceGateway


class BaseSourceGatewayProvider(ABC):

    @abstractmethod
    def source_from_url(self, url: str) -> Optional[BaseSourceGateway]:
        """:return source gateway pointing towards source that handles the url specified"""
