from functools import cached_property
import operator
from typing import NoReturn


class PropertiesClass:
    def __init__(self):
        self._read_only = "read only"
        self._fully_accessible = "fully accessible"
        self._undecorated = "undecorated"

    @property
    def read_only(self):
        """Read-only"""
        return self._read_only

    @property
    def fully_accessible(self):
        """Fully-accessible"""
        return self._fully_accessible

    @fully_accessible.setter
    def fully_accessible(self, v):
        self._fully_accessible = v

    @fully_accessible.deleter
    def fully_accessible(self):
        del self._fully_accessible

    def get_undecorated(self):
        return self._undecorated

    def set_undecorated(self, value):
        self._undecorated = value

    def delete_undecorated(self):
        del self._undecorated

    undecorated_property = property(get_undecorated, set_undecorated, delete_undecorated)

    def set_write_only(self, v):
        self._write_only = v

    def del_write_only(self):
        del self._write_only

    write_only = property(None, set_write_only, del_write_only, "Write-only")

    def raise_base_exception(self) -> NoReturn:
        raise BaseException("not derived from Exception")  # pylint: disable=broad-exception-raised

    @cached_property
    def cached_read_only(self):
        return self._read_only

    operator_read_only = property(operator.attrgetter("cached_read_only"))
