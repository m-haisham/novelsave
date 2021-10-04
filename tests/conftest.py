import pytest
from loguru import logger


@pytest.fixture(scope="session", autouse=True)
def disable_logger(request):
    logger.remove()

