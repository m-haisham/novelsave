import pytest

from novelsave.core.dtos import NovelDTO, ChapterDTO, MetaDataDTO
from novelsave.core.entities.novel import Novel, NovelUrl, Chapter, MetaData, Volume
from novelsave.utils.adapters import DTOAdapter


@pytest.fixture
def dto_adapter() -> DTOAdapter:
    return DTOAdapter()


def test_novel_from_dto(dto_adapter):
    novel_dto = NovelDTO(
        id=None,
        title="title",
        author="author",
        synopsis="a nice description",
        thumbnail_url="thumbnail",
        thumbnail_path=None,
        lang="language",
        url="link",
        last_updated=None,
    )

    expected_novel = Novel(
        title="title",
        author="author",
        synopsis="a nice description",
        thumbnail_url="thumbnail",
        lang="language",
    )

    expected_url = NovelUrl(
        url="link",
    )

    actual_novel, actual_url = dto_adapter.novel_from_dto(novel_dto)
    for attrib in {"title", "author", "synopsis", "thumbnail_url", "lang"}:
        assert getattr(expected_novel, attrib) == getattr(actual_novel, attrib)

    for attrib in {"url"}:
        assert getattr(expected_url, attrib) == getattr(actual_url, attrib)


def test_update_novel_from_dto(dto_adapter):
    novel_dto = NovelDTO(
        id=None,
        title="title",
        author="author",
        synopsis="a nice description",
        thumbnail_url="thumbnail",
        thumbnail_path=None,
        lang="language",
        url="link",
        last_updated=None,
    )

    expected_novel = Novel(
        title="title",
        author="author",
        synopsis="a nice description",
        thumbnail_url="thumbnail",
        lang="language",
    )

    actual_novel = dto_adapter.update_novel_from_dto(Novel(), novel_dto)
    for attrib in {"title", "author", "synopsis", "thumbnail_url", "lang"}:
        assert getattr(expected_novel, attrib) == getattr(actual_novel, attrib)


def test_chapter_from_dto(dto_adapter):
    volume = Volume(id=1)

    chapter_dto = ChapterDTO(
        index=1,
        title="chapter title",
        url="https://my.chapter.org",
        content="content",
    )

    expected_chapter = Chapter(
        id=None,
        index=1,
        title="chapter title",
        url="https://my.chapter.org",
        volume_id=volume.id,
    )

    actual_chapter = dto_adapter.chapter_from_dto(volume, chapter_dto)
    for attrib in {"id", "index", "title", "url", "volume_id"}:
        assert getattr(expected_chapter, attrib) == getattr(actual_chapter, attrib)


def test_chapter_to_dto(dto_adapter):
    test_chapter = Chapter(
        index=1,
        title="something",
        url="url",
    )

    expected_dto = ChapterDTO(
        index=1,
        title="something",
        url="url",
    )

    actual_dto = dto_adapter.chapter_to_dto(test_chapter)
    assert expected_dto == actual_dto


def test_metadata_from_dto(dto_adapter):
    novel = Novel(id=1)

    metadata_dto = MetaDataDTO(
        name="name",
        value="value",
        namespace="ns",
        others={"role": "this"},
    )

    expected_metadata = MetaData(
        name="name",
        value="value",
        namespace="ns",
        others='{"role": "this"}',
        novel_id=novel.id,
    )

    actual_metadata = dto_adapter.metadata_from_dto(novel, metadata_dto)
    for attrib in {"name", "value", "namespace", "others", "novel_id"}:
        assert getattr(expected_metadata, attrib) == getattr(actual_metadata, attrib)
