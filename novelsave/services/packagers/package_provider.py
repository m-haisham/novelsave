from typing import List, Set, Iterable

from novelsave.core.services.packagers import BasePackager, BasePackagerProvider


class PackagerProvider(BasePackagerProvider):

    def __init__(self, epub: BasePackager):
        self._packager = {epub}

    def keywords(self):
        return [keyword for p in self._packager for keyword in p.keywords()]

    def packagers(self) -> Set[BasePackager]:
        return self._packager

    def filter_packagers(self, keywords: List[str]) -> Set[BasePackager]:
        return {
            compiler
            for compiler in self._packager
            if any(k in keywords for k in compiler.keywords())
        }
