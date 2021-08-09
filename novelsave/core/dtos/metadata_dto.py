from dataclasses import dataclass, field


@dataclass
class MetaDataDTO:
    DEFAULT_NAMESPACE = 'DC'
    SOURCE_INTERNAL = 'int'
    SOURCE_EXTERNAL = 'ext'

    name: str
    value: str
    others: dict = field(default_factory=lambda: {})
    namespace: str = DEFAULT_NAMESPACE
    src: str = SOURCE_INTERNAL
