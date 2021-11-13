from pathlib import Path

import pytest

from novelsave.core.entities.novel import Novel
from novelsave.exceptions import SourceNotFoundException
from novelsave.services import PathService


@pytest.fixture
def novel_service(mocker):
    return mocker.patch("novelsave.core.services.BaseNovelService")


@pytest.fixture
def source_service(mocker):
    return mocker.patch("novelsave.core.services.source.BaseSourceService")


data_dir = Path("~/data")
save_dir = Path("~/test_novels")
division_rules = {".html": "web"}


def test_divide(source_service, novel_service):
    path_service = PathService(
        data_dir, save_dir, division_rules, novel_service, source_service
    )

    # when there is a specified directory
    r_path = Path("subdivide_test_dir/test_file.html")
    s_path = path_service.divide(r_path)
    assert Path(r_path).parent / "web" / "test_file.html" == s_path

    # when there is no specified directory
    r_path = Path("subdivide_test_dir/test_file.json")
    s_path = path_service.divide(r_path)
    assert Path(r_path) == s_path


def test_get_novel_path_no_source(source_service, novel_service):
    source_service.source_from_url.side_effect = SourceNotFoundException("")

    path_service = PathService(
        data_dir, save_dir, division_rules, novel_service, source_service
    )
    path = path_service.novel_save_path(Novel(title="novel"))

    assert save_dir / "novel" == path


def test_get_novel_path_with_source(mocker, source_service, novel_service):
    source_gateway = mocker.patch("novelsave.core.services.source.BaseSourceGateway")
    source_gateway.name = "source"

    source_service.source_from_url.return_value = source_gateway

    path_service = PathService(
        data_dir, save_dir, division_rules, novel_service, source_service
    )
    path = path_service.novel_save_path(Novel(title="novel"))

    assert save_dir / "source" / "novel" == path


def test_get_thumbnail_path(mocker, source_service, novel_service):
    novel = Novel(id=1, thumbnail_url="https://my.site/local%20assets/image.jpg")

    path_service = PathService(
        data_dir, save_dir, division_rules, novel_service, source_service
    )
    path = path_service.thumbnail_path(novel)

    assert data_dir / "1" / "cover.jpg" == path


def test_get_thumbnail_path_no_suffix(source_service, novel_service):
    novel = Novel(id=1, thumbnail_url="https://my.site/local%20assets/image")

    path_service = PathService(
        data_dir, save_dir, division_rules, novel_service, source_service
    )
    path = path_service.thumbnail_path(novel)

    assert data_dir / "1" / "cover" == path


def test_resolve_data_path(source_service, novel_service):
    path_service = PathService(
        data_dir, save_dir, division_rules, novel_service, source_service
    )

    test_paths = {
        Path("1/cover.jpg"): data_dir / Path("1/cover.jpg"),
        Path("../1/cover.jpg"): data_dir / Path("1/cover.jpg"),
        Path("./1/cover.jpg"): data_dir / Path("1/cover.jpg"),
    }

    for test_path, expected in test_paths.items():
        path = path_service.resolve_data_path(test_path)
        assert expected == path


def test_relative_to_data_dir(source_service, novel_service):
    test_path = data_dir / Path("file")

    path_service = PathService(
        data_dir, save_dir, division_rules, novel_service, source_service
    )
    path = path_service.relative_to_data_dir(test_path)

    assert Path("file") == path
