"""Subarea seed data.

The canonical complete seed is currently loaded from ``seed_compressed``.
Human-readable subarea modules will be split incrementally by domain.
"""

from .seed_compressed import SUBAREAS

__all__ = ["SUBAREAS"]
