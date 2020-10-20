from dataclasses import dataclass

from typing import List


@dataclass
class Chapter:
    no: float = None
    title: str = None
    paragraphs: List[str] = None
    url: str = None
