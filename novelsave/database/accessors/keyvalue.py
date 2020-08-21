from tinydb import where

from .interface import IAccessor


class KeyValueAccessor(IAccessor):
    """
    Adds Key value functionality to table access
    """

    KEY_ID = 'KEY'
    VALUE_ID = 'VALUE'

    def put(self, key, value):
        """
        Puts the data into table marked by unique identifier

        :param key: unique identifier
        :param value: json data
        :return: None
        """
        self.table.upsert(
            {
                KeyValueAccessor.KEY_ID: key,
                KeyValueAccessor.VALUE_ID: value
            },
            where(KeyValueAccessor.KEY_ID) == key
        )

    def get(self, key, default=None):
        """
        Returns the data corresponding to unique identifier

        :param key: unique identifier
        :param default: if key does not exist return this value
        :return: data corresponding to unique identifier

        :raises ValueError: if more than one value corresponds to key
        """
        docs = self.table.search(where(KeyValueAccessor.KEY_ID) == key)
        if len(docs) == 1:
            return docs[0][KeyValueAccessor.VALUE_ID]
        elif len(docs) > 1:
            raise ValueError(f'More than one value corresponds to key: {key}')
        else:
            return default

    def all(self) -> dict:
        """
        :return: all key value pairs in dict format
        """
        docs = self.table.search(where(KeyValueAccessor.KEY_ID).exists())

        return {
            doc[KeyValueAccessor.KEY_ID]: doc[KeyValueAccessor.VALUE_ID]
            for doc in docs
        }

    def remove(self, key):
        """
        Removes the data associated with unique identifier and the doc entry

        :param key: unique identifier
        :return: None
        """
        self.table.remove(where(KeyValueAccessor.KEY_ID) == key)
