from pathlib import Path

from novelsave.utils.helpers import config_helper


def test_version_2():
    test_data = {
        "version": 2,
        "config": {"novel.dir": "//path/to/file"},
    }

    expected_config = {"novel": {"dir": Path("//path/to/file")}}

    assert config_helper._version_2(test_data) == expected_config
