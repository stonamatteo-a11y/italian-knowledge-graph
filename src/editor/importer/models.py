"""Immutable values shared by ontology import components."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SourceNode:
    identifier: Any
    node_type: Any
    label: Any
    description: Any
    parent: Any
    language: Any = "it"
    aliases: Any = ()
    sources: Any = ()
    notes: Any = ()
    relations: Any = ()
    extra_fields: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ParsedOntology:
    format_name: str
    parser_name: str
    nodes: tuple[SourceNode, ...]


@dataclass(frozen=True, slots=True)
class CanonicalNode:
    identifier: str
    node_type: str
    label: str
    description: str
    parent: str | None
    language: str
    aliases: tuple[str, ...] = ()
    sources: tuple[dict[str, str], ...] = ()
    notes: tuple[str, ...] = ()
    relations: tuple[dict[str, str], ...] = ()

    def as_record(self) -> dict[str, object]:
        record: dict[str, object] = {
            "id": self.identifier,
            "label": self.label,
            "description": self.description,
            "language": self.language,
        }
        if self.parent is not None:
            record["parent_id"] = self.parent
        for field, value in (
            ("aliases", self.aliases),
            ("sources", self.sources),
            ("notes", self.notes),
            ("relations", self.relations),
        ):
            if value:
                record[field] = [dict(item) if isinstance(item, dict) else item for item in value]
        return record


@dataclass(frozen=True, slots=True)
class ConversionResult:
    nodes: tuple[CanonicalNode, ...]
    modifications: tuple[str, ...]
    warnings: tuple[str, ...]
    unmapped_types: tuple[str, ...]
    errors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ImportPreview:
    token: str | None
    format_name: str
    parser_name: str
    nodes_found: int
    relationships_found: int
    nodes_to_add: int
    modifications: tuple[str, ...]
    collisions: tuple[str, ...]
    duplicates: tuple[str, ...]
    warnings: tuple[str, ...]
    warning_options: tuple[tuple[str, str], ...]
    information: tuple[str, ...]
    unmapped_types: tuple[str, ...]
    errors: tuple[str, ...]

    @property
    def importable(self) -> bool:
        return not self.errors and not self.unmapped_types and self.token is not None

    def as_dict(self) -> dict[str, object]:
        return {
            "token": self.token,
            "format": self.format_name,
            "parser": self.parser_name,
            "nodes_found": self.nodes_found,
            "relationships_found": self.relationships_found,
            "nodes_to_add": self.nodes_to_add,
            "modifications": list(self.modifications),
            "collisions": list(self.collisions),
            "duplicates": list(self.duplicates),
            "warnings": list(self.warnings),
            "warning_options": [
                {"id": identifier, "message": message}
                for identifier, message in self.warning_options
            ],
            "information": list(self.information),
            "unmapped_types": list(self.unmapped_types),
            "errors": list(self.errors),
            "importable": self.importable,
        }


@dataclass(frozen=True, slots=True)
class ImportReport:
    filename: str
    format_name: str
    parser_name: str
    conversions: tuple[str, ...]
    warnings_handled: tuple[str, ...]
    errors_resolved: tuple[str, ...]
    files_modified: tuple[str, ...]
    nodes_added: int
    relationships_added: int

    def as_dict(self) -> dict[str, object]:
        return {
            "file": self.filename,
            "format": self.format_name,
            "parser": self.parser_name,
            "conversions": list(self.conversions),
            "warnings_handled": list(self.warnings_handled),
            "errors_resolved": list(self.errors_resolved),
            "files_modified": list(self.files_modified),
            "summary": {
                "nodes_added": self.nodes_added,
                "relationships_added": self.relationships_added,
            },
        }
