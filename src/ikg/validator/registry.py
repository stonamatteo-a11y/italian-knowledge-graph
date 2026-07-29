"""Validation rule registry."""

from __future__ import annotations

from collections.abc import Iterable

from .rules import ValidationRule


class RuleRegistry:
    """Store accepted validation rules with unique public identifiers."""

    def __init__(self, rules: Iterable[ValidationRule] = ()) -> None:
        self._rules: dict[str, ValidationRule] = {}
        for rule in rules:
            self.register(rule)

    def register(self, rule: ValidationRule) -> None:
        if rule.rule_id in self._rules:
            raise ValueError(f"Duplicate validation rule ID: {rule.rule_id}")
        self._rules[rule.rule_id] = rule

    def accepted_rules(self) -> tuple[ValidationRule, ...]:
        return tuple(self._rules[key] for key in sorted(self._rules))
