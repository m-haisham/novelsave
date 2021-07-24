from novelsave_sources import models as source_models
from novelsave import view_models


class SourceAdapter(object):
    """adapter responsible for converting models from view_models to source and vice versa"""

    def novel_from_source_to_view(self, novel: source_models.Novel) -> view_models.Novel:
        """convert novel from source to that of view_model"""

        arguments = {
            key: value
            for key, value in vars(novel).items()
            if key in {'title', 'url', 'author', 'synopsis', 'thumbnail_url', 'lang'}
        }

        return view_models.Novel(id=None, **arguments)

    def novel_from_view_to_source(self, novel: view_models.Novel) -> source_models.Novel:
        """convert novel from view_model to that of source"""

        arguments = {
            key: value
            for key, value in vars(novel).items()
            if key in {'title', 'url', 'author', 'synopsis', 'thumbnail_url', 'lang'}
        }

        return source_models.Novel(**arguments)
