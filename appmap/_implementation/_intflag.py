import enum


class _IntFlag(int, enum.Enum):
    """
    Implement just enough of 3.6's IntFlag functionality.  This class
    can go away once we drop support for 3.5
    """
    def __or__(self, other):
        return self.__class__(self.value | self.__class__(other).value)

    def __and__(self, other):
        return self.__class__(self.value & self.__class__(other).value)

    def __contains__(self, other):
        return other.value & self.value == other.value
