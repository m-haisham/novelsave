from dataclasses import dataclass, field
from typing import Union


@dataclass
class MetaData:
    name: str
    value: str
    namespace: Union[str, None] = None
    others: dict = field(default_factory=lambda: {})
