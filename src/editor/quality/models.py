"""Immutable quality-report models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class QualityIssue:
    identifier: str
    severity: str
    category: str
    node_id: str | None
    title: str
    detail: str

    def as_dict(self) -> dict[str, str | None]:
        return {
            "id": self.identifier,
            "severity": self.severity,
            "category": self.category,
            "node_id": self.node_id,
            "title": self.title,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class ChecklistItem:
    identifier: str
    label: str
    passed: bool
    node_ids: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.identifier,
            "label": self.label,
            "passed": self.passed,
            "node_ids": list(self.node_ids),
        }


@dataclass(frozen=True, slots=True)
class QualityContext:
    nodes: tuple[dict[str, Any], ...]
    edges: tuple[dict[str, str], ...]

    @property
    def by_id(self) -> dict[str, dict[str, Any]]:
        return {node["id"]: node for node in self.nodes}


@dataclass(frozen=True, slots=True)
class CheckResult:
    dimension: str
    score: float
    issues: tuple[QualityIssue, ...]
    checklist: tuple[ChecklistItem, ...]


@dataclass(frozen=True, slots=True)
class QualityReport:
    score: float
    dimensions: tuple[tuple[str, float], ...]
    issues: tuple[QualityIssue, ...]
    coverage: tuple[tuple[str, float | int], ...]
    statistics: tuple[tuple[str, int], ...]
    activity: tuple[dict[str, Any], ...]
    checklist: tuple[ChecklistItem, ...]

    def as_dict(self) -> dict[str, object]:
        issues = [issue.as_dict() for issue in self.issues]
        return {
            "score": self.score,
            "dimensions": dict(self.dimensions),
            "errors": [issue for issue in issues if issue["severity"] == "error"],
            "warnings": [issue for issue in issues if issue["severity"] == "warning"],
            "coverage": dict(self.coverage),
            "statistics": dict(self.statistics),
            "activity": list(self.activity),
            "checklist": [item.as_dict() for item in self.checklist],
        }
