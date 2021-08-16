import unittest
from unittest.mock import Mock

from novelsave.core.entities.novel import MetaData
from novelsave.services.compilers import EpubCompiler


class TestEpubCompiler(unittest.TestCase):

    def test_metadata_display_value(self):
        compiler = EpubCompiler(Mock(), Mock(), Mock())

        data = MetaData(name='name', value='value', namespace='DC', others='{"key":"value"}')
        value = compiler.metadata_display_value(data)
        self.assertEqual('value(key=value)', value)

        data = MetaData(name='name', value='value', namespace='DC', others='{}')
        value = compiler.metadata_display_value(data)
        self.assertEqual('value', value)
