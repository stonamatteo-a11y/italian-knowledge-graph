"""Immutable contribution preparation models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ContributionChanges:
    nodes_added: tuple[str, ...]
    nodes_modified: tuple[str, ...]
    nodes_removed: tuple[str, ...]
    relationships_added: tuple[tuple[str, str], ...]
    relationships_modified: tuple[tuple[str, str, str], ...]
    relationships_removed: tuple[tuple[str, str], ...]

    @property
    def changed(self) -> bool:
        return any(
            (
                self.nodes_added,
                self.nodes_modified,
                self.nodes_removed,
                self.relationships_added,
                self.relationships_modified,
                self.relationships_removed,
            )
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "nodes": {
                "added": list(self.nodes_added),
                "modified": list(self.nodes_modified),
                "removed": list(self.nodes_removed),
            },
            "relationships": {
                "added": [
                    {"source": source, "target": target}
                    for source, target in self.relationships_added
                ],
                "modified": [
                    {"target": target, "before": before, "after": after}
                    for target, before, after in self.relationships_modified
                ],
                "removed": [
                    {"source": source, "target": target}
                    for source, target in self.relationships_removed
                ],
            },
        }


@dataclass(frozen=True, slots=True)
class ContributionPreview:
    changes: ContributionChanges
    files: tuple[str, ...]
    diff: str
    errors: tuple[str, ...]
    warnings: tuple[dict[str, Any], ...]
    quality_before: float
    quality_after: float
    excluded: tuple[str, ...]
    git_available: bool
    git_blockers: tuple[str, ...]
    commit_title: str
    pull_request_body: str

    @property
    def preparable(self) -> bool:
        return self.changes.changed and not self.errors

    def as_dict(self) -> dict[str, object]:
        return {
            "changed": self.changes.changed,
            "preparable": self.preparable,
            "changes": self.changes.as_dict(),
            "files": list(self.files),
            "diff": self.diff,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "quality": {"before": self.quality_before, "after": self.quality_after},
            "excluded": list(self.excluded),
            "git": {
                "available": self.git_available,
                "blockers": list(self.git_blockers),
            },
            "commit_title": self.commit_title,
            "pull_request_body": self.pull_request_body,
        }
