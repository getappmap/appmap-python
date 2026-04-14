"""Test helpers"""


import importlib.metadata

from packaging import version as pkg_version


class DictIncluding(dict):
    """A dict that on comparison just checks whether the other dict includes
    all of its items. Any extra ones are ignored.

        >>> {'a': 5, 'b': 6} == DictIncluding({'a': 5})
        True
        >>> {'a': 6, 'b': 6} == DictIncluding({'a': 5})
        False

    This is especially useful for tests.
    """

    def __eq__(self, other):
        return other.items() >= self.items()


class HeadersIncluding(dict):
    """Like DictIncluding, but key comparison is case-insensitive."""

    def __eq__(self, other):
        for k in self.keys():
            v = other.get(k, other.get(k.lower(), None))
            if v is None:
                return False
        return True


def package_version(pkg):
    return pkg_version.parse(importlib.metadata.version(pkg))


def check_call_stack(events):
    """Ensure that the call stack in events has balanced call and return events"""
    stack = []
    for e in events:
        if e.get("event") == "call":
            stack.append(e)
        elif e.get("event") == "return":
            assert len(stack) > 0, f"return without call, {e.get('id')}"
            call = stack.pop()
            assert call.get("id") == e.get(
                "parent_id"
            ), f"parent mismatch, {call.get('id')} != {e.get('parent_id')}"
    assert len(stack) == 0, f"leftover events, {len(stack)}"


if __name__ == "__main__":
    import json
    from pathlib import Path
    import sys

    with Path(sys.argv[1]).open(encoding="utf-8") as f:
        appmap = json.load(f)
        check_call_stack(appmap["events"])
