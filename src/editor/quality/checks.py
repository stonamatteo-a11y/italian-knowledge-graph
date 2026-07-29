"""Built-in deterministic ontology quality checks."""

from __future__ import annotations

from collections import Counter, defaultdict

from validators.validate_ontology import validate_graph

from .models import ChecklistItem, CheckResult, QualityContext, QualityIssue


def _ratio(passed: int, total: int) -> float:
    return 100.0 if total == 0 else round(100 * passed / total, 1)


class CompletenessCheck:
    identifier = "quality.completeness"

    def evaluate(self, context: QualityContext) -> CheckResult:
        required = ("id", "type", "label", "description", "language")
        incomplete = [
            node["id"]
            for node in context.nodes
            if any(
                not isinstance(node.get(field), str) or not node[field].strip()
                for field in required
            )
        ]
        issues = tuple(
            QualityIssue(
                f"KQC-COMP-{index:04d}",
                "error",
                "completezza",
                node_id,
                "Proprietà obbligatorie incomplete",
                "Il nodo non contiene tutte le proprietà canoniche obbligatorie.",
            )
            for index, node_id in enumerate(sorted(incomplete), 1)
        )
        return CheckResult(
            "completezza",
            _ratio(len(context.nodes) - len(incomplete), len(context.nodes)),
            issues,
            (
                ChecklistItem(
                    self.identifier,
                    "Tutti i nodi hanno proprietà obbligatorie complete",
                    not incomplete,
                    tuple(sorted(incomplete)),
                ),
            ),
        )


class IntegrityCheck:
    identifier = "quality.integrity"

    def evaluate(self, context: QualityContext) -> CheckResult:
        errors = validate_graph(context.by_id, list(context.edges))
        identifiers = set(context.by_id)
        issues = []
        for index, detail in enumerate(sorted(errors), 1):
            candidate = detail.split(":", 1)[0]
            issues.append(
                QualityIssue(
                    f"KQC-INT-{index:04d}",
                    "error",
                    "integrità",
                    candidate if candidate in identifiers else None,
                    "Errore di integrità",
                    detail,
                )
            )
        return CheckResult(
            "integrità",
            max(0.0, 100.0 - 10.0 * len(issues)),
            tuple(issues),
            (
                ChecklistItem(
                    self.identifier,
                    "Gerarchia e riferimenti superano il Validator",
                    not issues,
                    tuple(issue.node_id for issue in issues if issue.node_id),
                ),
            ),
        )


class ConsistencyCheck:
    identifier = "quality.consistency"

    def evaluate(self, context: QualityContext) -> CheckResult:
        groups: dict[str, list[str]] = defaultdict(list)
        for node in context.nodes:
            groups[node["label"].strip().casefold()].append(node["id"])
        duplicates = sorted(
            node_id
            for identifiers in groups.values()
            if len(identifiers) > 1
            for node_id in identifiers
        )
        issues = tuple(
            QualityIssue(
                f"KQC-CONS-{index:04d}",
                "warning",
                "coerenza",
                node_id,
                "Label duplicata",
                "La stessa label canonica è utilizzata da più nodi.",
            )
            for index, node_id in enumerate(duplicates, 1)
        )
        return CheckResult(
            "coerenza",
            max(0.0, round(100.0 - 100 * len(duplicates) / max(len(context.nodes), 1), 1)),
            issues,
            (
                ChecklistItem(
                    self.identifier,
                    "Le label canoniche non sono duplicate",
                    not duplicates,
                    tuple(duplicates),
                ),
            ),
        )


class DocumentationCheck:
    identifier = "quality.documentation"
    minimum_length = 24

    def evaluate(self, context: QualityContext) -> CheckResult:
        short = sorted(
            node["id"]
            for node in context.nodes
            if len(node["description"].strip()) < self.minimum_length
        )
        issues = tuple(
            QualityIssue(
                f"KQC-DOC-{index:04d}",
                "warning",
                "documentazione",
                node_id,
                "Descrizione troppo breve",
                f"La descrizione contiene meno di {self.minimum_length} caratteri.",
            )
            for index, node_id in enumerate(short, 1)
        )
        return CheckResult(
            "documentazione",
            _ratio(len(context.nodes) - len(short), len(context.nodes)),
            issues,
            (
                ChecklistItem(
                    self.identifier,
                    "Le descrizioni hanno contenuto documentale sufficiente",
                    not short,
                    tuple(short),
                ),
            ),
        )


class CoverageCheck:
    identifier = "quality.coverage"

    def evaluate(self, context: QualityContext) -> CheckResult:
        children = Counter(
            node["parent_id"] for node in context.nodes if node.get("parent_id") is not None
        )
        expected = [node for node in context.nodes if node["type"] in {"macroarea", "area"}]
        uncovered = sorted(node["id"] for node in expected if not children[node["id"]])
        issues = tuple(
            QualityIssue(
                f"KQC-COV-{index:04d}",
                "warning",
                "copertura",
                node_id,
                "Ramo senza copertura",
                "Il nodo non contiene il livello canonico successivo.",
            )
            for index, node_id in enumerate(uncovered, 1)
        )
        return CheckResult(
            "copertura",
            _ratio(len(expected) - len(uncovered), len(expected)),
            issues,
            (
                ChecklistItem(
                    self.identifier,
                    "Macroaree e aree hanno almeno un figlio canonico",
                    not uncovered,
                    tuple(uncovered),
                ),
            ),
        )


BUILTIN_CHECKS = (
    CompletenessCheck(),
    IntegrityCheck(),
    ConsistencyCheck(),
    DocumentationCheck(),
    CoverageCheck(),
)
