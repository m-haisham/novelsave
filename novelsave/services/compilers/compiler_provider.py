from typing import List, Set, Iterable

from novelsave.core.services.compilers import BaseCompiler, BaseCompilerProvider


class CompilerProvider(BaseCompilerProvider):

    def __init__(self, epub: BaseCompiler):
        self._compilers = {epub}

    def keywords(self):
        return [keyword for compiler in self._compilers for keyword in compiler.keywords()]

    def compilers(self) -> Set[BaseCompiler]:
        return self._compilers

    def filter_compilers(self, keywords: List[str]) -> Set[BaseCompiler]:
        return {
            compiler
            for compiler in self._compilers
            if any(k in keywords for k in compiler.keywords)
        }
