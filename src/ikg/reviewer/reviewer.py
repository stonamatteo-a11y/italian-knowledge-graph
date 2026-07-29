"""Provider-neutral AI Reviewer orchestration."""

from __future__ import annotations

from collections.abc import Iterable

from ikg.graph import KnowledgeGraph

from .heuristic import HeuristicReviewerProvider
from .models import ReviewReport, ReviewSeverity
from .provider import ReviewerProvider

SEVERITY_ORDER = {
    ReviewSeverity.HIGH: 0,
    ReviewSeverity.MEDIUM: 1,
    ReviewSeverity.LOW: 2,
}


class AIReviewer:
    """Aggregate advisory providers into one immutable report."""

    def __init__(self, providers: Iterable[ReviewerProvider] | None = None) -> None:
        self._providers = (
            tuple(providers) if providers is not None else (HeuristicReviewerProvider(),)
        )

    def review(self, graph: KnowledgeGraph) -> ReviewReport:
        suggestions = [
            suggestion for provider in self._providers for suggestion in provider.review(graph)
        ]
        ordered = tuple(
            sorted(
                suggestions,
                key=lambda item: (
                    SEVERITY_ORDER[item.severity],
                    item.entity_id,
                    item.category,
                    item.id,
                ),
            )
        )
        return ReviewReport(suggestions=ordered)
