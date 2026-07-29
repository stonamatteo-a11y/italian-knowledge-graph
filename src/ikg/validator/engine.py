"""Deterministic validation engine."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .models import Finding, ValidationReport
from .rules import ValidationRule


class ValidationEngine:
    """Run registered rules in stable order and build an immutable report."""

    def __init__(self, rules: Iterable[ValidationRule]) -> None:
        self._rules = tuple(sorted(rules, key=lambda rule: rule.rule_id))

    def validate(self, graph: Any) -> ValidationReport:
        findings: list[Finding] = []
        for rule in self._rules:
            findings.extend(rule.validate(graph))

        ordered = tuple(
            sorted(
                findings,
                key=lambda item: (
                    item.rule_id,
                    item.severity.value,
                    item.location,
                    item.message,
                ),
            )
        )
        return ValidationReport(findings=ordered)
