import atexit

from dependency_injector.wiring import inject, Provide
from loguru import logger

from novelsave.containers import Application
from novelsave.core.services.source import BaseSourceService


@atexit.register
@inject
def update_check_event(
        source_service: BaseSourceService = Provide[Application.services.source_service],
):
    logger.debug("Checking for new sources version...")

    try:
        latest_version = source_service.get_latest_version()
    except ConnectionError as e:
        logger.exception(e)
        return

    if latest_version <= source_service.current_version:
        logger.debug(f"Source package is upto date (local={source_service.current_version}, pypi={latest_version}).")
        return

    logger.warning(f"Sources package has a new version available ({latest_version}), "
                   f"run the following command to upgrade.\n"
                   f"   python -m pip install --upgrade novelsave-sources")
