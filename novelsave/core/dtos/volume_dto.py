from dataclasses import dataclass, field
from typing import List, Optional

from .chapter_dto import ChapterDTO


@dataclass
class VolumeDTO:
    id: Optional[int]
    index: int
    name: str

    chapters: List[ChapterDTO] = field(default_factory=lambda: [])
