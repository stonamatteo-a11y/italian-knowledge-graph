"""Immutable advisory review models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReviewSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True, slots=True)
class ReviewSuggestion:
    id: str
    severity: ReviewSeverity
    category: str
    entity_id: str
    title: str
    explanation: str
    confidence: float


@dataclass(frozen=True, slots=True)
class ReviewReport:
    suggestions: tuple[ReviewSuggestion, ...]
