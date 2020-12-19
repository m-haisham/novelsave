from dataclasses import dataclass, field

from typing import Dict

@dataclass
class Novel:
    title: str = None
    author: str = None
    synopsis: str = None
    thumbnail: str = None
    metadata: Dict[str, Dict[str, str]] = field(default_factory=lambda: {})
    url: str = None
