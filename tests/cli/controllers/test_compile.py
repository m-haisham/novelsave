from unittest.mock import MagicMock

import pytest

from novelsave.client.cli import controllers


@pytest.fixture
def packager_provider():
    return MagicMock()


@pytest.fixture
def path_service():
    return MagicMock()


def test_compile_no_novel(mocker, packager_provider, path_service):
    mocker.patch(
        "novelsave.client.cli.controllers._package.get_novel", side_effect=ValueError()
    )

    with pytest.raises(SystemExit):
        controllers.package(
            "https://novel.site", ["epub"], False, packager_provider, path_service
        )


def test_compile_with_novel(mocker, packager_provider, path_service):
    mocker.patch(
        "novelsave.client.cli.controllers._package.get_novel", return_value="novel"
    )

    controllers.package(
        "https://novel.site", ["epub"], False, packager_provider, path_service
    )
