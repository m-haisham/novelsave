from webnovel.models import Novel

from ..accessors import KeyValueAccessor


class InfoAccess(KeyValueAccessor):
    _table_name = 'info'

    fields = ['id', 'title', 'synopsis', 'author', 'url', 'cover_url']

    def set_info(self, novel: Novel):
        """
        saves the fields (InfoAccess.fields) from novel

        :param novel: object to save
        :return: None
        """
        for field in InfoAccess.fields:
            self.put(field, getattr(novel, field))

    def get_info(self) -> Novel:
        """
        :return: saved novel info
        """

        # filter out any unwanted fields
        data = {key: value for key, value in self.all().items() if key in InfoAccess.fields}

        return Novel(**data)
