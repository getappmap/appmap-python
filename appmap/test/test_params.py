"""Tests for the function parameter handling"""

# pylint: disable=missing-function-docstring

import inspect
import sys

import pytest

import vendor.wrapt.src.appmap.wrapt as wrapt
from appmap._implementation.event import CallEvent
from appmap._implementation.importer import FilterableCls, FilterableFn

empty_args = {"name": "args", "class": "builtins.tuple", "kind": "rest", "value": "()"}

empty_kwargs = {
    "name": "kwargs",
    "class": "builtins.dict",
    "kind": "keyrest",
    "size": 0,
    "value": "{}",
}


class _params:
    def __init__(self, C):
        self.C = C

    @classmethod
    def prepare(cls, ffn):
        fn = ffn.obj
        make_call_event = CallEvent.make(fn, ffn.fntype)
        params = CallEvent.make_params(ffn)

        def wrapped_fn(_, instance, args, kwargs):
            return make_call_event(
                parameters=CallEvent.set_params(params, instance, args, kwargs)
            )

        return wrapped_fn

    def wrap_test_func(self, fnname):
        C = self.C
        static_fn = inspect.getattr_static(C, fnname)
        fn = getattr(C, fnname)
        fc = FilterableCls(C)
        ffn = FilterableFn(fc, fn, static_fn)
        wrapped = self.prepare(ffn)
        wrapt.wrap_function_wrapper(C, fnname, wrapped)


@pytest.mark.usefixtures("with_data_dir", autouse=True)
class TestMethodBase:
    @pytest.fixture
    def params(self, request):
        """
        Manage the lifecycle of the params module.  Import it before users
        of this fixture, unload it after.  This ensures that each test
        sees a pristine version of the classes it contains.
        """
        from params import (  # pyright: ignore[reportMissingImports] pylint: disable=import-error
            C,
        )

        p = _params(C)
        p.wrap_test_func(request.param)
        yield p
        del sys.modules["params"]

    def assert_receiver(self, evt, expected):
        r = evt.receiver

        # object_id is always present
        r.pop("object_id")

        # value is always present, but we might not know what it
        # should be
        if "value" not in expected:
            r.pop("value")

        assert r == expected

    def assert_parameter(self, evt, idx, expected):
        parameter = evt.parameters[idx]

        # object_id is always present
        parameter.pop("object_id")

        assert parameter == expected


class TestStaticMethods(TestMethodBase):
    @pytest.mark.parametrize("params", ["static"], indirect=True)
    def test_no_receiver(self, params):
        evt = params.C.static("param")
        assert not evt.receiver

    @pytest.mark.parametrize("params", ["static"], indirect=True)
    def test_one_param(self, params):
        evt = params.C.static("static")
        assert len(evt.parameters) == 1
        parameter = evt.parameters[0]

        parameter.pop("object_id")

        assert parameter == {
            "name": "p",
            "class": "builtins.str",
            "kind": "req",
            "value": "'static'",
        }


class TestClassMethods(TestMethodBase):
    @pytest.mark.parametrize("params", ["cls"], indirect=True)
    def test_one_param(self, params):
        evt = params.C.cls("cls")
        assert len(evt.parameters) == 1

        self.assert_receiver(
            evt,
            {
                "name": "cls",
                "class": "builtins.type",
                "kind": "req",
                "value": "<class 'params.C'>",
            },
        )

        self.assert_parameter(
            evt,
            0,
            {"name": "p", "class": "builtins.str", "kind": "req", "value": "'cls'"},
        )


class TestInstanceMethods(TestMethodBase):
    @pytest.mark.parametrize("params", ["zero"], indirect=True)
    def test_no_args(self, params):
        evt = params.C().zero()
        assert len(evt.parameters) == 0
        self.assert_receiver(evt, {"name": "self", "class": "params.C", "kind": "req"})

    @pytest.mark.parametrize(
        "params,arg,expected",
        [
            ("one", "world", ("builtins.str", "'world'")),
            ("one", None, ("builtins.NoneType", "None")),
        ],
        indirect=["params"],
    )
    def test_one_param(self, params, arg, expected):
        evt = params.C().one(arg)
        assert len(evt.parameters) == 1

        expected_type, expected_value = expected
        self.assert_parameter(
            evt,
            0,
            {
                "name": "p",
                "class": expected_type,
                "kind": "req",
                "value": expected_value,
            },
        )

    @staticmethod
    @pytest.mark.parametrize("params", ["one"], indirect=True)
    def test_one_arg_missing(params):
        evt = params.C().one()
        assert len(evt.parameters) == 0

    @pytest.mark.parametrize("params", ["one"], indirect=True)
    def test_one_receiver_none(self, params):
        evt = params.C.one(None, 1)
        assert len(evt.parameters) == 1

        assert evt.receiver == {
            "name": "self",
            "kind": "req",
            "class": "builtins.NoneType",
            "object_id": evt.receiver["object_id"],
            "value": "None",
        }

        self.assert_parameter(
            evt, 0, {"name": "p", "class": "builtins.int", "kind": "req", "value": "1"}
        )

    @pytest.mark.parametrize(
        "params,arg,expected",
        [
            ("one", "world", ("builtins.str", "'world'")),
            ("one", None, ("builtins.NoneType", "None")),
        ],
        indirect=["params"],
    )
    def test_one_param_kw(self, params, arg, expected):
        evt = params.C().one(p=arg)
        assert len(evt.parameters) == 1

        expected_type, expected_value = expected
        self.assert_parameter(
            evt,
            0,
            {
                "name": "p",
                "class": expected_type,
                "kind": "req",
                "value": expected_value,
            },
        )

    @pytest.mark.parametrize("params", ["args_kwargs"], indirect=True)
    def test_optional_no_args(self, params):
        evt = params.C().args_kwargs()
        assert len(evt.parameters) == 2

        self.assert_receiver(evt, {"name": "self", "class": "params.C", "kind": "req"})

        self.assert_parameter(evt, 0, empty_args)
        self.assert_parameter(evt, 1, empty_kwargs)

    @pytest.mark.parametrize("params", ["args_kwargs"], indirect=True)
    def test_optional_2_positional(self, params):
        evt = params.C().args_kwargs(1, 2)
        assert len(evt.parameters) == 2

        self.assert_parameter(
            evt,
            0,
            {
                "name": "args",
                "class": "builtins.tuple",
                "kind": "rest",
                "value": "(1, 2)",
            },
        )

    @pytest.mark.parametrize("params", ["args_kwargs"], indirect=True)
    def test_optional_2_keyword(self, params):
        evt = params.C().args_kwargs(p1=1, p2=2)
        assert len(evt.parameters) == 2

        # pre 3.6, python doesn't preserve order of **kwargs. We don't
        # care about the order, though, so just check to make sure the
        # parameters have the correct values
        value = evt.parameters[1].pop("value")
        d = eval(value)  # pylint: disable=eval-used
        assert d["p1"] == 1 and d["p2"] == 2

        self.assert_parameter(
            evt,
            1,
            {
                "name": "kwargs",
                "class": "builtins.dict",
                "kind": "keyrest",
                "size": 2,
            },
        )

    @pytest.mark.skipif(
        sys.version_info < (3, 8), reason="positional-only added in 3.8"
    )
    @pytest.mark.parametrize("params", ["positional_only"], indirect=True)
    def test_positional_only(self, params):
        evt = params.C().positional_only(1, 2)
        assert len(evt.parameters) == 2

        self.assert_parameter(
            evt, 0, {"class": "builtins.int", "kind": "req", "name": "p1", "value": "1"}
        )

        self.assert_parameter(
            evt, 1, {"class": "builtins.int", "kind": "req", "name": "p2", "value": "2"}
        )

    @pytest.mark.skipif(sys.version_info < (3, 8), reason="keyword-only added in 3.8")
    @pytest.mark.parametrize("params", ["keyword_only"], indirect=True)
    def test_keyword_only(self, params):
        evt = params.C().keyword_only(p2=2, p1=1)
        assert len(evt.parameters) == 2

        self.assert_parameter(
            evt,
            0,
            {"class": "builtins.int", "kind": "keyreq", "name": "p1", "value": "1"},
        )

        self.assert_parameter(
            evt,
            1,
            {"class": "builtins.int", "kind": "keyreq", "name": "p2", "value": "2"},
        )

    @pytest.mark.parametrize("params", ["with_defaults"], indirect=True)
    def test_keywords_with_defaults(self, params):
        evt = params.C().with_defaults()
        assert len(evt.parameters) == 2

        self.assert_parameter(
            evt, 0, {"class": "builtins.int", "kind": "opt", "name": "p1", "value": "1"}
        )

        self.assert_parameter(
            evt, 1, {"class": "builtins.int", "kind": "opt", "name": "p2", "value": "2"}
        )

    @pytest.mark.parametrize("params", ["with_defaults"], indirect=True)
    def test_keywords_defaults_with_args(self, params):
        evt = params.C().with_defaults(p1=3, p2=4)
        assert len(evt.parameters) == 2

        self.assert_parameter(
            evt, 0, {"class": "builtins.int", "kind": "opt", "name": "p1", "value": "3"}
        )

        self.assert_parameter(
            evt, 1, {"class": "builtins.int", "kind": "opt", "name": "p2", "value": "4"}
        )
