from dataclasses import dataclass

from typing import List, Union, Tuple


@dataclass
class Chapter:
    id: int
    index: int
    title: str
    url: str
    paragraphs: Union[str, List[str]] = None
    volume: Tuple[int, str] = None

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return all((self.index == other.index, self.url == other.url))
