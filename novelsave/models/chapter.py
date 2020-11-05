from dataclasses import dataclass

from typing import List, Tuple, Union


@dataclass
class Chapter:
    index: int = -1
    no: float = None
    title: str = None
    paragraphs: Union[str, List[str]] = None
    url: str = None

    @property
    def order(self) -> Tuple[int, float]:
        return self.index, self.no

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url
