from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class BaseCalibreService(ABC):

    @abstractmethod
    def ebook_convert(self, input_file: Path, output_file: Path, pass_args: List[str] = None):
        """convert ebook file from the input type to output type"""
