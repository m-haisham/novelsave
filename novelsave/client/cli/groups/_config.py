import sys

import click
from dependency_injector.wiring import inject, Provide
from loguru import logger

from ..main import cli
from novelsave.containers import Application
from novelsave.core.services.config import BaseConfigService


@cli.group(name="config")
def _config():
    """Manage customizable configurations."""


@_config.command(name="show")
@click.option("--key", help="View configuration for only this key.")
@inject
def _show_config(
    key: str,
    config_service: BaseConfigService = Provide[Application.services.config_service],
):
    """View the current configuration."""
    if key is not None:
        try:
            value = config_service.get_config(key)
        except KeyError as e:
            logger.error(str(e).strip('"'))
            sys.exit(1)

        logger.info(f"'{key}': {value}")
        return

    for key, value in config_service.get_all_configs().items():
        logger.info(f"'{key}': {value}")


@_config.command(name="set")
@click.argument("key")
@click.option("--value", required=True, help="New value for the configuration.")
@inject
def _set_config(
    key,
    value,
    config_service: BaseConfigService = Provide[Application.services.config_service],
):
    """Change the configuration value."""
    try:
        config_service.set_config(key, value)
    except KeyError as e:
        logger.error(str(e).strip('"'))
        sys.exit(1)

    logger.info(f"'{key}' set to '{value}'.")


@_config.command(name="reset")
@click.argument("key")
@inject
def _reset_config(
    key,
    config_service: BaseConfigService = Provide[Application.services.config_service],
):
    """Reset the configuration back to default."""
    try:
        config_service.reset_config(key)
    except KeyError as e:
        logger.error(str(e).strip('"'))
        sys.exit(1)

    logger.info(f"Reset '{key}' to default value '{config_service.get_config(key)}').")
