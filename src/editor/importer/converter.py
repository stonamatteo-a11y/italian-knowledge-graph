"""Convert parsed external nodes into the canonical IKG model."""

from __future__ import annotations

import re
import unicodedata

from ikg.metadata import MetadataError, canonical_metadata

from .mapping import MappingEngine
from .models import CanonicalNode, ConversionResult, ParsedOntology


def _identifier(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9_]+", "_", ascii_value.casefold())).strip("_")


class CanonicalConverter:
    def __init__(self, mapping_engine: MappingEngine | None = None) -> None:
        self.mapping_engine = mapping_engine or MappingEngine()

    def convert(
        self,
        parsed: ParsedOntology,
        mappings: dict[str, str] | None = None,
    ) -> ConversionResult:
        modifications: list[str] = []
        warnings: list[str] = []
        errors: list[str] = []
        unmapped_types: set[str] = set()
        identifier_map: dict[str, str] = {}

        for index, node in enumerate(parsed.nodes):
            if not isinstance(node.identifier, str) or not node.identifier.strip():
                errors.append(f"Node {index + 1}: missing or invalid ID")
                continue
            converted = _identifier(node.identifier)
            if not converted:
                errors.append(f"{node.identifier!r}: ID cannot be converted")
                continue
            identifier_map[node.identifier] = converted
            if converted != node.identifier:
                modifications.append(f"ID {node.identifier!r} → {converted!r}")

        converted_nodes: list[CanonicalNode] = []
        for index, node in enumerate(parsed.nodes):
            if not isinstance(node.identifier, str) or node.identifier not in identifier_map:
                continue
            location = node.identifier or f"node {index + 1}"
            node_type = node.node_type
            if isinstance(node_type, str):
                canonical_type = self.mapping_engine.resolve(node_type, mappings)
            else:
                errors.append(f"{location}: type must be a non-empty string")
                continue
            if canonical_type is None:
                unmapped_types.add(node_type)
                continue
            if canonical_type != node_type:
                modifications.append(f"{location}: type {node_type!r} → {canonical_type!r}")
            if not isinstance(node.label, str) or not node.label.strip():
                errors.append(f"{location}: label must be a non-empty string")
                continue
            if not isinstance(node.description, str) or not node.description.strip():
                errors.append(f"{location}: description must be a non-empty string")
                continue
            if not isinstance(node.language, str) or node.language != "it":
                errors.append(f"{location}: language must be 'it'")
                continue
            if node.parent is not None and not isinstance(node.parent, str):
                errors.append(f"{location}: parent must be a string or null")
                continue
            parent = (
                identifier_map.get(node.parent, _identifier(node.parent)) if node.parent else None
            )
            if node.extra_fields:
                warnings.append(
                    f"{location}: ignored non-canonical fields: {', '.join(node.extra_fields)}"
                )
            metadata_input = {
                "id": identifier_map[node.identifier],
                "label": node.label,
                "aliases": node.aliases,
                "sources": node.sources,
                "notes": node.notes,
                "relations": node.relations,
            }
            try:
                metadata = canonical_metadata(metadata_input)
            except MetadataError as exc:
                errors.append(f"{location}: {exc}")
                continue
            converted_nodes.append(
                CanonicalNode(
                    identifier_map[node.identifier],
                    canonical_type,
                    node.label,
                    node.description,
                    parent,
                    node.language,
                    tuple(metadata["aliases"]),
                    tuple(metadata["sources"]),
                    tuple(metadata["notes"]),
                    tuple(metadata["relations"]),
                )
            )
        return ConversionResult(
            tuple(converted_nodes),
            tuple(sorted(set(modifications))),
            tuple(sorted(set(warnings))),
            tuple(sorted(unmapped_types, key=str.casefold)),
            tuple(sorted(set(errors))),
        )
