from abc import ABC, abstractmethod
from pathlib import Path


class BaseFileService(ABC):

    @abstractmethod
    def write_str(self, path: Path, data: str):
        """write and replace strings to a file"""

    @abstractmethod
    def write_bytes(self, path: Path, data: bytes):
        """write and replace bytes to a file"""

    @abstractmethod
    def read_str(self, path: Path) -> str:
        """read strings from a file"""

    @abstractmethod
    def read_bytes(self, path: Path) -> bytes:
        """read bytes from a file"""
