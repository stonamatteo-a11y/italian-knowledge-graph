"""Contracts for deterministic validation rules."""

from __future__ import annotations

from typing import Any, Protocol

from .models import Finding


class ValidationRule(Protocol):
    """A deterministic, side-effect-free validation rule."""

    rule_id: str

    def validate(self, graph: Any) -> tuple[Finding, ...]:
        """Return every finding produced for the supplied graph."""
        ...
