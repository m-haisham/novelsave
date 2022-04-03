from unittest.mock import Mock

import pytest
from novelsave_sources import novel_source_types

from novelsave.exceptions import SourceNotFoundException
from novelsave.services.source import SourceService


@pytest.fixture
def source_service():
    return SourceService(Mock())


def test_source_from_url(source_service):
    source_service = source_service.source_from_url(
        novel_source_types()[0].base_urls[0]
    )
    assert source_service is not None


def test_source_from_url_unavailable(source_service):
    with pytest.raises(SourceNotFoundException):
        source_service.source_from_url("https://test.site")
