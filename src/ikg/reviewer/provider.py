"""Provider contract for advisory review implementations."""

from __future__ import annotations

from typing import Protocol

from ikg.graph import KnowledgeGraph

from .models import ReviewSuggestion


class ReviewerProvider(Protocol):
    """Return non-binding suggestions without modifying the graph."""

    def review(self, graph: KnowledgeGraph) -> tuple[ReviewSuggestion, ...]:
        """Review a graph and return advisory suggestions."""
