import sys

from dependency_injector.wiring import inject, Provide
from loguru import logger

from novelsave.cli.helpers import get_novel
from novelsave.containers import Application
from novelsave.core.services.compilers import BaseCompilerProvider


@inject
def compile(
        id_or_url: str,
        compiler_provider: BaseCompilerProvider = Provide[Application.compilers.compiler_provider],
):
    """
    compile the selected novel into the formats of choosing

    Note: currently supports epub format only

    :return: None
    """
    novel = get_novel(id_or_url)
    if novel is None:
        sys.exit(1)

    for compiler in compiler_provider.compilers():
        path = compiler.compile(novel)
        logger.info(f'Compiled (keywords: {compiler.keywords()}, loc="{path}")')
