from abc import ABC, abstractmethod
from pathlib import Path

from novelsave.core.entities.novel import Novel


class BaseSaveService(ABC):

    @abstractmethod
    def get_novel_path(self, novel: Novel) -> Path:
        """:return novel save directory"""
