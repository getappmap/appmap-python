"""Tests for methods decorated with @property"""

# pyright: reportMissingImports=false
# pylint: disable=import-error,import-outside-toplevel
import pytest
from _appmap.test.helpers import DictIncluding

pytestmark = pytest.mark.appmap_enabled

@pytest.fixture(autouse=True)
def setup(with_data_dir):  # pylint: disable=unused-argument
    # with_data_dir sets up sys.path so properties_class can be imported
    pass


def test_getter_instrumented(events):
    from properties_class import PropertiesClass

    ec = PropertiesClass()

    actual = PropertiesClass.read_only.__doc__
    assert actual == "Read-only"

    assert ec.read_only == "read only"

    with pytest.raises(AttributeError, match=r".*(has no setter|can't set attribute).*"):
        ec.read_only = "not allowed"

    with pytest.raises(AttributeError, match=r".*(has no deleter|can't delete attribute).*"):
        del ec.read_only

    assert len(events) == 2
    assert events[0].to_dict() == DictIncluding({
        "event": "call",
        "defined_class": "properties_class.PropertiesClass",
        "method_id": "read_only (get)",
    })


def test_accessible_instrumented(events):
    from properties_class import PropertiesClass

    ec = PropertiesClass()
    assert PropertiesClass.fully_accessible.__doc__ == "Fully-accessible"

    assert ec.fully_accessible == "fully accessible"

    ec.fully_accessible = "updated"
    # Check the value of the attribute directly, to avoid extra events
    assert ec._fully_accessible == "updated"  # pylint: disable=protected-access

    del ec.fully_accessible

    assert len(events) == 6
    assert events[0].to_dict() == DictIncluding({
        "event": "call",
        "defined_class": "properties_class.PropertiesClass",
        "method_id": "fully_accessible (get)",
    })

    assert events[2].to_dict() == DictIncluding({
        "event": "call",
        "defined_class": "properties_class.PropertiesClass",
        "method_id": "fully_accessible (set)",
    })

    assert events[4].to_dict() == DictIncluding({
        "event": "call",
        "defined_class": "properties_class.PropertiesClass",
        "method_id": "fully_accessible (del)",
    })


def test_writable_instrumented(events):
    from properties_class import PropertiesClass

    ec = PropertiesClass()
    assert PropertiesClass.write_only.__doc__ == "Write-only"

    with pytest.raises(AttributeError, match=r".*(has no getter|unreadable attribute).*"):
        _ = ec.write_only

    ec.write_only = "updated example"

    assert len(events) == 2
    assert events[0].to_dict() == DictIncluding({
        "event": "call",
        "defined_class": "properties_class.PropertiesClass",
        "method_id": "set_write_only (set)",
    })


def test_operator_attrgetter(events):
    from properties_class import PropertiesClass

    ec = PropertiesClass()

    assert ec.operator_read_only == "read only"

    with pytest.raises(AttributeError, match=r".*(has no setter|can't set attribute).*"):
        ec.operator_read_only = "not allowed"

    with pytest.raises(AttributeError, match=r".*(has no deleter|can't delete attribute).*"):
        del ec.operator_read_only

    assert len(events) == 2
    assert events[0].to_dict() == DictIncluding({
        "event": "call",
        "defined_class": "properties_class.PropertiesClass",
        "method_id": "operator_read_only (get)",
    })

def test_operator_itemgetter(events):
    from properties_class import PropertiesClass

    ec = PropertiesClass()
    assert ec.taste == "yum"
    assert len(events) == 2
    assert events[0].to_dict() == DictIncluding({
        "event": "call",
        # operator.itemgetter.__module__ isn't available before 3.10
        # "defined_class": "operator",
        "method_id": "itemgetter (get)",
    })


def test_free_function(events):
    from properties_class import PropertiesClass

    ec = PropertiesClass()
    assert ec.free_read_only_prop == "read only"
    assert len(events) == 2
    assert events[0].to_dict() == DictIncluding({
        "event": "call",
        "defined_class": "properties_class",
        "method_id": "free_read_only (get)",
    })


@pytest.mark.xfail(
    raises=AssertionError,
    reason="needs fix for https://github.com/getappmap/appmap-python/issues/365",
)
def test_functools_partial(events):
    from properties_class import PropertiesClass

    PropertiesClass.static_partial_method()
    assert len(events) > 0