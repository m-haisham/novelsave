import sys

from dependency_injector.wiring import inject, Provide
from loguru import logger

from novelsave.cli.helpers import get_novel
from novelsave.containers import Application
from novelsave.core.services.packagers import BasePackagerProvider


@inject
def package(
        id_or_url: str,
        packager_provider: BasePackagerProvider = Provide[Application.packagers.packager_provider],
):
    """
    package the selected novel into the formats of choosing

    Note: currently supports epub format only

    :return: None
    """
    try:
        novel = get_novel(id_or_url)
    except ValueError:
        sys.exit(1)

    for packager in packager_provider.packagers():
        path = packager.package(novel)
        logger.info(f'Compiled (keywords: {packager.keywords()}, loc="{path}")')
