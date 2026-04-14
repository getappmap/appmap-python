"""
Test util functionality
"""

import uuid
from pathlib import Path

from _appmap.utils import locate_file_up, scenario_filename


def test_scenario_filename__short():
    """leaves short names alone"""
    assert scenario_filename("foobar") == "foobar"


def test_scenario_filename__special_character():
    """has a customizable suffix"""
    assert scenario_filename("foobar?=65") == "foobar_65"

def test_locate_file_up(data_dir):
    result = locate_file_up("appmap.yml", Path(data_dir) / "package1" / "package2")
    assert result.parts[-3:] == ("_appmap", "test", "data")

    result = locate_file_up("test_util.py", Path(data_dir) / "package1" / "package2")
    assert result.parts[-2:] == ("_appmap", "test")

    impossible_file_name = str(uuid.uuid4()) + ".yml"
    result = locate_file_up(impossible_file_name, data_dir)
    assert result is None
