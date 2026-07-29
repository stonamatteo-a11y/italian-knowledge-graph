"""Immutable result models used by the validation engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass(frozen=True, slots=True, order=True)
class Finding:
    rule_id: str
    severity: Severity
    message: str
    location: str = ""


@dataclass(frozen=True, slots=True)
class ValidationReport:
    findings: tuple[Finding, ...]

    @property
    def is_valid(self) -> bool:
        return not any(item.severity is Severity.ERROR for item in self.findings)

    @property
    def error_count(self) -> int:
        return sum(item.severity is Severity.ERROR for item in self.findings)

    @property
    def warning_count(self) -> int:
        return sum(item.severity is Severity.WARNING for item in self.findings)

    @property
    def info_count(self) -> int:
        return sum(item.severity is Severity.INFO for item in self.findings)
