from pathlib import Path

import click
from dependency_injector.wiring import inject, Provide
from loguru import logger

from ..main import cli
from ...containers import Application
from ...core.services.config import BaseConfigService


@cli.group(name='config')
def _config():
    """Manage customizable configurations"""


@_config.group(name='novel_dir')
def _novel_dir():
    """Manage configuration novel save location"""


@_novel_dir.command(name='set')
@click.argument('path')
@inject
def _set_novel_dir(path, config_service: BaseConfigService = Provide[Application.services.config_service]):
    """Set novel save location"""
    config_service.set_novel_dir(Path(path))
    logger.info(f"Novel save directory has been updated ({path=})")


@_novel_dir.command(name='reset')
@inject
def _reset_novel_dir(config_service: BaseConfigService = Provide[Application.services.config_service]):
    """Reset novel save location to default"""
    config_service.reset_novel_dir()
    logger.info(f"Novel save directory has been reset (path={config_service.get_novel_dir()})")
