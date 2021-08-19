import sys

from dependency_injector.wiring import Provide, inject
from loguru import logger

from novelsave.containers import Application
from novelsave.core.services.source import BaseMetaSourceGateway, BaseSourceGateway, BaseSourceGatewayProvider
from novelsave.exceptions import NovelSourceNotFoundException


@inject
def get_source_gateway(
        url: str,
        source_provider: BaseSourceGatewayProvider = Provide[Application.services.source_gateway_provider],
) -> BaseSourceGateway:
    try:
        source_gateway = source_provider.source_from_url(url)
    except NovelSourceNotFoundException:
        logger.error(f"Could not find source corresponding to url ({url=}).")
        sys.exit(1)

    logger.debug(f"Acquired source (name='{source_gateway.name}').")
    return source_gateway


@inject
def get_meta_source_gateway(
        url: str,
        source_provider: BaseSourceGatewayProvider = Provide[Application.services.source_gateway_provider],
) -> BaseMetaSourceGateway:
    try:
        meta_source_gateway = source_provider.meta_source_from_url(url)
    except NovelSourceNotFoundException:
        logger.error(f"Could not find metadata source corresponding to url ({url=}).")
        sys.exit(1)

    logger.debug(f"Acquired metadata source (name='{meta_source_gateway.name}').")
    return meta_source_gateway
