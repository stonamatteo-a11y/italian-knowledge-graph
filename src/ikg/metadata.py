"""Canonical optional ontology metadata normalization and validation."""

from __future__ import annotations

import json
import unicodedata
from datetime import date, datetime
from typing import Any
from urllib.parse import urlparse

REGISTERED_PREDICATES = frozenset({"CONTAINS"})
METADATA_FIELDS = ("aliases", "sources", "notes", "relations")
SOURCE_FIELDS = ("url", "title", "publisher", "accessed_at", "note")
RELATION_FIELDS = ("predicate", "target_id", "note")


class MetadataError(ValueError):
    """Raised when optional canonical metadata is malformed."""


def _normalized_text(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold()


def _strings(values: Any, field: str) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, (list, tuple)):
        raise MetadataError(f"{field} must be a list")
    result: dict[str, str] = {}
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise MetadataError(f"{field} must contain non-empty strings")
        result.setdefault(_normalized_text(value), value.strip())
    return [result[key] for key in sorted(result)]


def normalize_aliases(values: Any, label: str) -> list[str]:
    aliases = _strings(values, "aliases")
    if any(_normalized_text(alias) == _normalized_text(label) for alias in aliases):
        raise MetadataError("aliases must not contain the primary label")
    return aliases


def normalize_notes(values: Any) -> list[str]:
    return _strings(values, "notes")


def _valid_uri(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme and (parsed.netloc or parsed.path))


def _valid_iso_date(value: str) -> bool:
    try:
        if "T" in value:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            date.fromisoformat(value)
    except ValueError:
        return False
    return True


def normalize_sources(values: Any) -> list[dict[str, str]]:
    if values is None:
        return []
    if not isinstance(values, (list, tuple)):
        raise MetadataError("sources must be a list")
    unique: dict[str, dict[str, str]] = {}
    for value in values:
        if not isinstance(value, dict):
            raise MetadataError("sources must contain objects")
        unknown = sorted(set(value) - set(SOURCE_FIELDS))
        if unknown:
            raise MetadataError(f"source has unknown fields: {', '.join(unknown)}")
        source: dict[str, str] = {}
        for field in SOURCE_FIELDS:
            item = value.get(field)
            if item is None or item == "":
                continue
            if not isinstance(item, str) or not item.strip():
                raise MetadataError(f"source field {field!r} must be a non-empty string")
            source[field] = item.strip()
        if not source:
            raise MetadataError("source must not be empty")
        if "url" in source and not _valid_uri(source["url"]):
            raise MetadataError(f"invalid source URL/URI: {source['url']!r}")
        if "accessed_at" in source and not _valid_iso_date(source["accessed_at"]):
            raise MetadataError(f"invalid source accessed_at date: {source['accessed_at']!r}")
        key = json.dumps(source, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        unique[key] = source
    return [unique[key] for key in sorted(unique)]


def normalize_relations(
    values: Any, node_id: str, known_ids: set[str] | None = None
) -> list[dict[str, str]]:
    if values is None:
        return []
    if not isinstance(values, (list, tuple)):
        raise MetadataError("relations must be a list")
    unique: dict[tuple[str, str, str], dict[str, str]] = {}
    for value in values:
        if not isinstance(value, dict):
            raise MetadataError("relations must contain objects")
        unknown = sorted(set(value) - set(RELATION_FIELDS))
        if unknown:
            raise MetadataError(f"relation has unknown fields: {', '.join(unknown)}")
        predicate = value.get("predicate")
        target_id = value.get("target_id")
        note = value.get("note")
        if not isinstance(predicate, str) or not predicate.strip():
            raise MetadataError("relation predicate must be a non-empty string")
        if not isinstance(target_id, str) or not target_id.strip():
            raise MetadataError("relation target_id must be a non-empty string")
        predicate = predicate.strip().upper()
        target_id = target_id.strip()
        if predicate not in REGISTERED_PREDICATES:
            raise MetadataError(f"unknown relation predicate: {predicate!r}")
        if known_ids is not None and target_id not in known_ids:
            raise MetadataError(f"relation target does not exist: {target_id!r}")
        if target_id == node_id:
            raise MetadataError("self relation is not allowed")
        relation = {"predicate": predicate, "target_id": target_id}
        if note is not None and note != "":
            if not isinstance(note, str) or not note.strip():
                raise MetadataError("relation note must be a non-empty string")
            relation["note"] = note.strip()
        key = (predicate, target_id, relation.get("note", ""))
        unique[key] = relation
    return [unique[key] for key in sorted(unique)]


def canonical_metadata(
    node: dict[str, Any],
    known_ids: set[str] | None = None,
) -> dict[str, list[Any]]:
    """Return deterministic optional metadata, omitting nothing supplied."""
    return {
        "aliases": normalize_aliases(node.get("aliases"), str(node.get("label", ""))),
        "sources": normalize_sources(node.get("sources")),
        "notes": normalize_notes(node.get("notes")),
        "relations": normalize_relations(node.get("relations"), str(node.get("id", "")), known_ids),
    }
