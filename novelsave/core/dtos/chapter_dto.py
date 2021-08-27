from dataclasses import dataclass

from typing import List, Union, Tuple, Optional


@dataclass
class ChapterDTO:
    index: int
    title: str
    url: str
    content: Union[str, List[str]] = None
    volume: Tuple[int, str] = None
