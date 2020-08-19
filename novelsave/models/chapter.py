from dataclasses import dataclass

from typing import List


@dataclass
class Chapter:
    no: int = None
    title: str = None
    paragraphs: List[str] = None
    url: str = None
