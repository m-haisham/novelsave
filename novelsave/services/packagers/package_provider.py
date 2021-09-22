from typing import List, Set, Iterable, Tuple

from novelsave.core.services.packagers import BasePackager, BasePackagerProvider


class PackagerProvider(BasePackagerProvider):

    def __init__(self, *args):
        self._packagers = args

    def keywords(self):
        return [keyword for p in self._packagers for keyword in p.keywords()]

    def packagers(self) -> Iterable[BasePackager]:
        return self._packagers

    def filter_packagers(self, keywords: Iterable[str]) -> Iterable[BasePackager]:
        keywords = [k.lower() for k in keywords]
        packagers = self.packagers()

        filtered = set()
        for keyword in keywords:
            for p in packagers:
                if keyword in p.keywords():
                    filtered.add(p)
                    break
            else:  # if inner loop was not broken
                raise ValueError(f"No packager was found that matches '{keyword}'.")

        return sorted(filtered, key=lambda p: p.priority)
