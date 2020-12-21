from dataclasses import dataclass, field
from typing import Union


@dataclass
class MetaData:
    name: str
    value: str
    others: dict = field(default_factory=lambda: {})
    namespace: str = 'DC'

    DEFAULT_NAMESPACE = 'DC'
