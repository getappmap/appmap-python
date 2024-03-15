"""Test helpers"""


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
