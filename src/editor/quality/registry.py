"""Extensible quality-check registry."""

from __future__ import annotations

from typing import Protocol

from .models import CheckResult, QualityContext


class QualityCheck(Protocol):
    identifier: str

    def evaluate(self, context: QualityContext) -> CheckResult: ...


class QualityRegistry:
    def __init__(self, checks: tuple[QualityCheck, ...] = ()) -> None:
        self._checks: dict[str, QualityCheck] = {}
        for check in checks:
            self.register(check)

    def register(self, check: QualityCheck) -> None:
        if check.identifier in self._checks:
            raise ValueError(f"Duplicate quality check: {check.identifier}")
        self._checks[check.identifier] = check

    def evaluate(self, context: QualityContext) -> tuple[CheckResult, ...]:
        return tuple(
            self._checks[identifier].evaluate(context) for identifier in sorted(self._checks)
        )
