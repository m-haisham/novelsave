import requests
from dependency_injector.wiring import inject, Provide
from loguru import logger

from novelsave.containers import Application
from novelsave.core.services import BaseMetaService
from novelsave.core.services.source import BaseSourceService


@inject
def update_check_event(
        source_service: BaseSourceService = Provide[Application.services.source_service],
        meta_service: BaseMetaService = Provide[Application.services.meta_service],
):
    logger.debug("Checking for new package versions...")

    if type(source_service) == Provide:
        logger.debug("Service injection failed. Exiting process silently.")
        return

    available_updates = []
    errors = []

    try:   # novelsave-sources
        latest_sources_version = source_service.get_latest_version()
        if latest_sources_version > source_service.current_version:
            available_updates.append(('novelsave-sources', latest_sources_version))
    except requests.ConnectionError as e:
        errors.append(e)
        logger.debug(f"Connection terminated unexpectedly while checking for update (package='novelsave-sources').")

    try:  # novelsave
        latest_version = meta_service.get_latest_version()
        if latest_version > meta_service.current_version:
            available_updates.append(('novelsave', latest_version))
    except requests.ConnectionError as e:
        errors.append(e)
        logger.debug(f"Connection terminated unexpectedly while checking for update (package='novelsave').")

    if not available_updates:
        logger.debug(f'No upgrades to packages detected (errors={len(errors)}).')
        return

    logger.warning(
        f"Following packages have new versions available: {', '.join(f'{n}=={v}' for n, v in available_updates)}.\n"
        f"Run the following command to upgrade:\n"
        f"   python -m pip install --upgrade {' '.join(n for n, v in available_updates)}")
