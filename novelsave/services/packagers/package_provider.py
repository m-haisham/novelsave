from typing import List, Set, Iterable, Tuple

from novelsave.core.services.packagers import BasePackager, BasePackagerProvider


class PackagerProvider(BasePackagerProvider):

    def __init__(self, epub: BasePackager, html: BasePackager):
        self._packagers = (epub, html)

    def keywords(self):
        return [keyword for p in self._packagers for keyword in p.keywords()]

    def packagers(self) -> Iterable[BasePackager]:
        return self._packagers

    def filter_packagers(self, keywords: Iterable[str]) -> Iterable[BasePackager]:
        keywords = [k.lower() for k in keywords]
        packagers = {
            compiler
            for compiler in self._packagers
            if any(k in keywords for k in compiler.keywords())
        }

        return sorted(packagers, key=lambda p: p.priority)
