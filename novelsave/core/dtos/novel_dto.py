from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class NovelDTO:
    id: Optional[int]
    title: str
    url: str
    author: str = '<Not specified>'
    synopsis: str = None

    thumbnail_url: str = None
    thumbnail_path: str = None

    lang: str = 'en'
    last_updated: datetime = None
