from dataclasses import dataclass, field


@dataclass
class MetaData:
    DEFAULT_NAMESPACE = 'DC'
    SOURCE_INTERNAL = 'int'
    SOURCE_EXTERNAL = 'ext'

    name: str
    value: str
    others: dict = field(default_factory=lambda: {})
    namespace: str = DEFAULT_NAMESPACE

    # 'int' short for internet/online
    src: str = 'int'
