from dataclasses import dataclass, field


@dataclass
class MetaData:
    name: str
    value: str
    others: dict = field(default_factory=lambda: {})
    namespace: str = 'DC'
    src: str = 'int'

    DEFAULT_NAMESPACE = 'DC'
    SOURCE_INTERNAL = 'int'
    SOURCE_EXTERNAL = 'ext'
