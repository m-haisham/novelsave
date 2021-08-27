from typing import List, Set, Iterable, Tuple

from novelsave.core.services.packagers import BasePackager, BasePackagerProvider


class PackagerProvider(BasePackagerProvider):

    def __init__(self, epub: BasePackager):
        self._packagers = (epub, )

    def keywords(self):
        return [keyword for p in self._packagers for keyword in p.keywords()]

    def packagers(self) -> Tuple[BasePackager]:
        return self._packagers

    def filter_packagers(self, keywords: List[str]) -> Set[BasePackager]:
        return {
            compiler
            for compiler in self._packagers
            if any(k in keywords for k in compiler.keywords())
        }
