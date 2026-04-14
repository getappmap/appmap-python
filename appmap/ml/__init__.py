"""Machine learning utilities for appmap.

This package contains small, dependency-light implementations of
algorithms useful for experimentation, such as SGD for strongly convex
objectives.
"""
from .strongly_convex import sgd_strongly_convex

__all__ = ["sgd_strongly_convex"]
