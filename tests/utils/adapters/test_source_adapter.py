import pytest
from novelsave_sources import models as sm

from novelsave.core import dtos
from novelsave.utils.adapters import SourceAdapter


@pytest.fixture
def source_adapter() -> SourceAdapter:
    return SourceAdapter()


def test_novel_to_internal(source_adapter):
    test_novel = sm.Novel(
        title="title",
        author="author",
        synopsis=["a nice description"],
        thumbnail_url="thumbnail",
        lang="language",
        url="link",
    )

    expected_novel = dtos.NovelDTO(
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

    actual_novel = source_adapter.novel_to_internal(test_novel)
    assert expected_novel == actual_novel


def test_chapter_to_internal(source_adapter):
    test_chapter = sm.Chapter(
        index=1,
        no=20,
        title="title",
        paragraphs="paragraphs this is",
        url="https://",
    )

    expected_chapter = dtos.ChapterDTO(
        index=1,
        title="title",
        content="paragraphs this is",
        url="https://",
    )

    actual_chapter = source_adapter.chapter_to_internal(test_chapter)
    assert expected_chapter == actual_chapter


def test_chapter_from_internal(source_adapter):
    test_chapter = dtos.ChapterDTO(
        index=1,
        title="title",
        content="paragraphs this is",
        url="https://",
    )

    expected_chapter = sm.Chapter(
        index=1,
        no=20,
        title="title",
        paragraphs="paragraphs this is",
        url="https://",
    )

    actual_chapter = source_adapter.chapter_to_external(test_chapter)
    assert expected_chapter == actual_chapter


def test_chapter_content_to_internal(source_adapter):
    test_chapter = sm.Chapter(
        index=1,
        no=20,
        title="title",
        paragraphs="paragraphs this is",
        url="https://",
    )

    expected_chapter = dtos.ChapterDTO(
        index=-1,
        title="",
        url="",
    )
    assert expected_chapter.content is None

    source_adapter.chapter_content_to_internal(test_chapter, expected_chapter)
    assert test_chapter.paragraphs == expected_chapter.content


def test_metadata_to_internal(source_adapter):
    test_metadata = sm.Metadata(
        name="name",
        value="value",
        others={"role": "something"},
    )

    expected_metadata = dtos.MetaDataDTO(
        name="name",
        value="value",
        others={"role": "something"},
        namespace="OPF",
    )

    actual_metadata = source_adapter.metadata_to_internal(test_metadata)
    assert expected_metadata == actual_metadata
