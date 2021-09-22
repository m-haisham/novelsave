import sys
from typing import Iterable

from dependency_injector.wiring import inject, Provide
from loguru import logger

from novelsave.cli.helpers import get_novel
from novelsave.containers import Application
from novelsave.core.services import BasePathService
from novelsave.core.services.packagers import BasePackagerProvider
from novelsave.exceptions import RequirementException, ToolException


@inject
def package(
        id_or_url: str,
        targets: Iterable[str],
        target_all: bool,
        packager_provider: BasePackagerProvider = Provide[Application.packagers.packager_provider],
        path_service: BasePathService = Provide[Application.services.path_service],
):
    """Package the selected novel into the formats of choosing"""
    if target_all:
        packagers = packager_provider.packagers()
    else:
        try:
            packagers = packager_provider.filter_packagers(targets)
        except ValueError as e:
            logger.error(e)
            sys.exit(1)

    try:
        novel = get_novel(id_or_url)
    except ValueError:
        sys.exit(1)

    for packager in packagers:
        try:
            path = packager.package(novel)
        except (ToolException, RequirementException, FileNotFoundError) as e:
            logger.error(f"Packaging failed (type='{packager.keywords()[0]}').")
            logger.exception(e)
        else:
            logger.info(f"Packaging completed (type='{packager.keywords()[0]}', path='{path_service.relative_to_novel_dir(path)}').")
