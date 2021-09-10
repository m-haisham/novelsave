from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from .metadata_dto import MetaDataDTO
from .volume_dto import VolumeDTO


@dataclass
class NovelDTO:
    id: Optional[int]
    title: str
    url: str
    author: str = None
    synopsis: str = None

    thumbnail_url: str = None
    thumbnail_path: str = None

    lang: str = 'en'
    last_updated: datetime = None

    volumes: List[VolumeDTO] = field(default_factory=lambda: [])
    metadata: List[MetaDataDTO] = field(default_factory=lambda: [])
