import os
from pathlib import Path
from typing import Union, Optional

_path_type = Union[str, Path, os.PathLike]


class FileService(object):

    def __init__(self, location: Path):
        self.location = location

    def _get_relative(self, r_path: _path_type) -> Path:
        """create the directories if they dont exist and return the actual path"""
        path = self.location / r_path
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def write_str(self, r_path: _path_type, data: str):
        """write and replace strings to a file"""
        path = self._get_relative(r_path)
        with path.open('w') as file:
            file.write(data)

    def write_bytes(self, r_path: _path_type, data: bytes):
        """write and replace bytes to a file"""
        path = self._get_relative(r_path)
        with path.open('wb') as file:
            file.write(data)

    def read_str(self, r_path: _path_type) -> str:
        """read strings from a file, returns none if file doesnt exist"""
        path = self._get_relative(r_path)
        if not path.is_file():
            raise FileNotFoundError()

        with path.open('r') as file:
            return file.read()

    def read_bytes(self, r_path: _path_type) -> bytes:
        """read bytes from a file, returns none is file doesnt exist"""
        path = self._get_relative(r_path)
        if not path.is_file():
            raise FileNotFoundError()

        with path.open('rb') as file:
            return file.read()
