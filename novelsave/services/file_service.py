from pathlib import Path

from novelsave.core.services import BaseFileService


class FileService(BaseFileService):

    def write_str(self, path: Path, data: str):
        """write and replace strings to a file"""
        with path.open('w') as file:
            file.write(data)

    def write_bytes(self, path: Path, data: bytes):
        """write and replace bytes to a file"""
        with path.open('wb') as file:
            file.write(data)

    def read_str(self, path: Path) -> str:
        """read strings from a file"""
        with path.open('r') as file:
            return file.read()

    def read_bytes(self, path: Path) -> bytes:
        """read bytes from a file"""
        with path.open('rb') as file:
            return file.read()
