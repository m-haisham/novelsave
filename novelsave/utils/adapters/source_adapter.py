from novelsave_sources import models as sm
from novelsave.models import source_models as im


class SourceAdapter(object):
    """adapter responsible for converting models from view_models to source and vice versa"""

    def novel_to_internal(self, novel: sm.Novel) -> im.Novel:
        """convert novel from internal to source"""

        arguments = {
            key: value
            for key, value in vars(novel).items()
            if key in {'title', 'url', 'author', 'synopsis', 'thumbnail_url', 'lang'}
        }

        return im.Novel(id=None, **arguments)

    def novel_from_internal(self, novel: im.Novel) -> sm.Novel:
        """convert novel from source to internal"""

        arguments = {
            key: value
            for key, value in vars(novel).items()
            if key in {'title', 'url', 'author', 'synopsis', 'thumbnail_url', 'lang'}
        }

        return sm.Novel(**arguments)

    def chapter_to_internal(self, chapter: sm.Chapter) -> im.Chapter:
        """convert chapter from source to internal"""

        return im.Chapter(
            id=None,
            index=chapter.index,
            title=chapter.title,
            url=chapter.url,
            content=chapter.paragraphs,
            volume=chapter.volume,
        )

    def chapter_from_internal(self, chapter: im.Chapter) -> sm.Chapter:
        """convert chapter from internal to source"""

        return sm.Chapter(
            index=chapter.index,
            title=chapter.title,
            url=chapter.url,
            paragraphs=chapter.content,
            volume=chapter.volume,
        )

    def metadata_to_internal(self, metadata: sm.Metadata) -> im.MetaData:
        """convert metadata from source to internal"""

        return im.MetaData(
            name=metadata.name,
            value=metadata.value,
            namespace=metadata.namespace,
            others=metadata.others,
        )

    def metadata_from_internal(self, metadata: im.MetaData) -> sm.Metadata:
        """convert metadata from internal to source"""

        return sm.Metadata(
            name=metadata.name,
            value=metadata.value,
            namespace=metadata.namespace,
            others=metadata.others,
        )

    def chapter_content_to_internal(self, source_chapter: sm.Chapter, internal_chapter: im.Chapter):
        """map content from source chapter to internal chapter"""
        internal_chapter.content = source_chapter.paragraphs
