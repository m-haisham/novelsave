import unittest
from unittest.mock import Mock

from novelsave.core.entities.novel import MetaData
from novelsave.services.packagers import EpubPackager


class TestEpubCompiler(unittest.TestCase):

    def test_metadata_display_value(self):
        compiler = EpubPackager(Mock(), Mock(), Mock(), Mock())

        data = MetaData(name='name', value='value', namespace='DC', others='{"key":"value"}')
        value = compiler.metadata_display_value(data)
        self.assertEqual('value(key=value)', value)

        data = MetaData(name='name', value='value', namespace='DC', others='{}')
        value = compiler.metadata_display_value(data)
        self.assertEqual('value', value)
