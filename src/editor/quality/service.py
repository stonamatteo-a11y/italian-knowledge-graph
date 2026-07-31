"""Knowledge Quality Center report aggregation."""

from __future__ import annotations

from collections import Counter
from typing import Any

from ..store import LEVELS
from .checks import BUILTIN_CHECKS
from .models import QualityContext, QualityReport
from .registry import QualityRegistry


class KnowledgeQualityCenter:
    def __init__(self, registry: QualityRegistry | None = None) -> None:
        self.registry = registry or QualityRegistry(BUILTIN_CHECKS)

    def evaluate(
        self,
        records: dict[str, list[dict[str, Any]]],
        activity: tuple[dict[str, Any], ...] = (),
    ) -> QualityReport:
        nodes = []
        edges = []
        for section, node_type, _ in LEVELS:
            for record in records[section]:
                parent = record.get("parent_id")
                nodes.append({**record, "type": node_type, "parent_id": parent})
                if parent is not None:
                    edges.append({"source": parent, "target": record["id"], "relation": "CONTAINS"})
                for relation in record.get("relations", []):
                    edges.append(
                        {
                            "source": record["id"],
                            "target": relation["target_id"],
                            "relation": relation["predicate"],
                        }
                    )
        context = QualityContext(tuple(nodes), tuple(edges))
        results = self.registry.evaluate(context)
        dimensions = tuple(sorted((result.dimension, result.score) for result in results))
        score = (
            round(sum(value for _, value in dimensions) / len(dimensions), 1) if dimensions else 0.0
        )
        issues = tuple(
            sorted(
                (issue for result in results for issue in result.issues),
                key=lambda issue: (
                    0 if issue.severity == "error" else 1,
                    issue.category,
                    issue.node_id or "",
                    issue.identifier,
                ),
            )
        )
        checklist = tuple(
            item
            for result in sorted(results, key=lambda result: result.dimension)
            for item in result.checklist
        )
        type_counts = Counter(node["type"] for node in nodes)
        covered_parents = {node["parent_id"] for node in nodes if node.get("parent_id") is not None}
        branch_nodes = [node for node in nodes if node["type"] in {"macroarea", "area"}]
        coverage = (
            ("covered_branches", len(covered_parents & {node["id"] for node in branch_nodes})),
            ("total_branches", len(branch_nodes)),
            (
                "percentage",
                _coverage_percentage(branch_nodes, covered_parents),
            ),
        )
        statistics = (
            ("nodes", len(nodes)),
            ("relationships", len(edges)),
            ("macroareas", type_counts["macroarea"]),
            ("areas", type_counts["area"]),
            ("subareas", type_counts["sottoarea"]),
            ("errors", sum(issue.severity == "error" for issue in issues)),
            ("warnings", sum(issue.severity == "warning" for issue in issues)),
            ("nodes_with_sources", sum(bool(node.get("sources")) for node in nodes)),
            ("nodes_without_sources", sum(not node.get("sources") for node in nodes)),
            (
                "source_coverage_percentage",
                round(100 * sum(bool(node.get("sources")) for node in nodes) / len(nodes), 1)
                if nodes
                else 100.0,
            ),
            ("aliases", sum(len(node.get("aliases", [])) for node in nodes)),
            ("nodes_with_duplicate_aliases", 0),
            (
                "semantic_relations",
                sum(len(node.get("relations", [])) for node in nodes),
            ),
            ("invalid_relations", 0),
            ("nodes_with_notes", sum(bool(node.get("notes")) for node in nodes)),
        )
        return QualityReport(
            score,
            dimensions,
            issues,
            coverage,
            statistics,
            tuple(activity),
            checklist,
        )


def _coverage_percentage(
    branch_nodes: list[dict[str, Any]],
    covered_parents: set[str],
) -> float:
    if not branch_nodes:
        return 100.0
    covered = sum(node["id"] in covered_parents for node in branch_nodes)
    return round(100 * covered / len(branch_nodes), 1)
