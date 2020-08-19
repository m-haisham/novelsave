from dataclasses import dataclass


@dataclass
class Novel:
    title: str = None
    author: str = None
    synopsis: str = None
    thumbnail: str = None
    url: str = None
