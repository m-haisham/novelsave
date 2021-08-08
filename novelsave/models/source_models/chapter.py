from dataclasses import dataclass

from typing import List, Union, Tuple, Optional


@dataclass
class Chapter:
    id: Optional[int]
    index: int
    title: str
    url: str
    content: Union[str, List[str]] = None
    volume: Tuple[int, str] = None
