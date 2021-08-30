import atexit

from requests.exceptions import ConnectionError
from dependency_injector.wiring import inject, Provide
from loguru import logger

from novelsave.containers import Application
from novelsave.core.services import BaseMetaService
from novelsave.core.services.source import BaseSourceService


@atexit.register
@inject
def update_check_event(
        source_service: BaseSourceService = Provide[Application.services.source_service],
        meta_service: BaseMetaService = Provide[Application.services.meta_service],
):
    logger.debug("Checking for new package versions...")

    available_updates = []
    errors = []

    try:
        latest_sources_version = source_service.get_latest_version()
        if latest_sources_version > source_service.current_version:
            available_updates.append(('novelsave-sources', latest_sources_version))
    except ConnectionError as e:
        errors.append(e)
        logger.debug(f"Connection error during checking for updates (package='novelsave-sources').")

    try:
        latest_version = meta_service.get_latest_version()
        if latest_version > meta_service.current_version:
            available_updates.append(('novelsave', latest_version))
    except ConnectionError as e:
        errors.append(e)
        logger.debug(f"Connection error during checking for updates (package='novelsave').")

    if not available_updates:
        logger.debug(f'No upgrades to packages detected (errors={len(errors)}).')
        return

    logger.warning(
        f"Following packages have new versions available: {', '.join(f'{n}=={v}' for n, v in available_updates)}.\n"
        f"   python -m pip install --upgrade {' '.join(n for n, v in available_updates)}")
