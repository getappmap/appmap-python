"""Lightweight regex compilation boost with caching and optional faster backend.

This module provides a cached `compile` function that uses the `regex`
third-party package if available, falling back to the stdlib `re` module.
It caches compiled patterns to avoid repeated compilation overhead.
"""
from functools import lru_cache
import importlib
from typing import Pattern, Any

try:
    re_mod = importlib.import_module("regex")
except Exception:
    import re as re_mod


@lru_cache(maxsize=512)
def compile(pattern: str, flags: int = 0) -> Pattern[Any]:
    """Compile and cache a regex pattern.

    Args:
        pattern: regex pattern string
        flags: compilation flags

    Returns:
        A compiled regex pattern object.
    """
    return re_mod.compile(pattern, flags)


def cached_search(pattern: str, string: str, flags: int = 0):
    """Search `string` using a cached compiled pattern."""
    return compile(pattern, flags).search(string)


def cached_match(pattern: str, string: str, flags: int = 0):
    """Match `string` using a cached compiled pattern."""
    return compile(pattern, flags).match(string)


# Compatibility helpers so this module can be used as a drop-in replacement
# for the stdlib `re` in modules that call `import re` and then use
# `re.match`, `re.search`, or `re.compile`.
def match(pattern: str, string: str, flags: int = 0):
    return cached_match(pattern, string, flags)


def search(pattern: str, string: str, flags: int = 0):
    return cached_search(pattern, string, flags)


def findall(pattern: str, string: str, flags: int = 0):
    return compile(pattern, flags).findall(string)


def sub(pattern: str, repl, string: str, count: int = 0, flags: int = 0):
    return compile(pattern, flags).sub(repl, string, count=count)


__all__ = ["compile", "match", "search", "findall", "sub"]
