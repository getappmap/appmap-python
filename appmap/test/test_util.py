"""
Test util functionality
"""

from appmap._implementation.utils import scenario_filename


def test_scenario_filename__short():
    """leaves short names alone"""
    assert scenario_filename("foobar") == "foobar"


def test_scenario_filename__special_character():
    """has a customizable suffix"""
    assert scenario_filename("foobar?=65") == "foobar_65"
