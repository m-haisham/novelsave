import os
from pathlib import Path
from typing import Union, Dict

_path_type = Union[str, Path, os.PathLike]


class FileService(object):

    def __init__(self, data_dir: Path, data_division: Dict[str, str]):
        self.data_dir = data_dir
        self.data_division = data_division

    def from_relative(self, r_path: _path_type, mkdir=False) -> Path:
        """create the directories if specified and return the actual path"""
        path = self.data_dir / r_path
        if mkdir:
            path.parent.mkdir(parents=True, exist_ok=True)

        return path

    def apply_division(self, r_path: _path_type) -> Path:
        """add additional sub folder to the parent depending on the file type"""
        path = Path(r_path)
        parent = path.parent / self.data_division.get(path.suffix, '')

        return parent.resolve() / path.name

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
