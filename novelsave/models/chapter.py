from dataclasses import dataclass

from typing import List, Tuple


@dataclass
class Chapter:
    index: int = None
    no: float = None
    title: str = None
    paragraphs: List[str] = None
    url: str = None
    bulk: bool = False

    @property
    def order(self) -> Tuple[int, float]:
        return self.index, self.no
