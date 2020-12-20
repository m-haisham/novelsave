from dataclasses import dataclass, field


@dataclass
class MetaData:
    name: str
    value: str
    namespace: str = None
    others: dict = field(default_factory=lambda: {})
