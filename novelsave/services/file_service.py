import os
from pathlib import Path
from typing import Union, Optional, Dict

_path_type = Union[str, Path, os.PathLike]


class FileService(object):

    def __init__(self, location: Path, data_division: Dict[str, str]):
        self.location = location
        self.data_division = data_division

    def from_relative(self, r_path: _path_type, mkdir=False) -> Path:
        """create the directories if they dont exist and return the actual path"""
        path = self.location / r_path
        if mkdir:
            path.parent.mkdir(parents=True, exist_ok=True)

        return path

    def apply_division(self, r_path: _path_type) -> Path:
        path = Path(r_path)
        return (path.parent / self.data_division.get(path.suffix, '')).resolve() / path.name

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
        if not path.is_file():
            raise FileNotFoundError()

        with path.open('r') as file:
            return file.read()

    def read_bytes(self, path: Path) -> bytes:
        """read bytes from a file"""
        if not path.is_file():
            raise FileNotFoundError()

        with path.open('rb') as file:
            return file.read()
