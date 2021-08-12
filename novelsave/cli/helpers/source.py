import sys

from dependency_injector.wiring import Provide, inject
from loguru import logger

from novelsave.containers import Application
from novelsave.services.source import SourceGateway, SourceGatewayProvider


@inject
def get_source_gateway(
        url: str,
        source_provider: SourceGatewayProvider = Provide[Application.services.source_gateway_provider],
) -> SourceGateway:
    source_gateway = source_provider.source_from_url(url)
    if source_gateway is None:
        logger.error(f'Could not find source corresponding to url, {url}.')
        sys.exit(1)

    logger.debug(f'Acquired source (name={source_gateway.source_name()}).')
    return source_gateway
