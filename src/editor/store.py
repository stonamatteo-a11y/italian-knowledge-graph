"""Canonical ontology working copy and persistence."""

from __future__ import annotations

import copy
import json
import os
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any

from scripts.generate_seed import (
    OUTPUT_PATH,
    SeedGenerationError,
    load_canonical,
    render_seed_module,
    validate_canonical_schema,
)
from validators.validate_ontology import validate_graph

LEVELS = (
    ("macroareas", "macroarea", "macroareas.json"),
    ("areas", "area", "areas.json"),
    ("subareas", "sottoarea", "subareas.json"),
)
# Future concepts support extends this ordered level definition and canonical loader.
TYPE_TO_SECTION = {node_type: section for section, node_type, _ in LEVELS}
SECTION_TO_TYPE = {section: node_type for section, node_type, _ in LEVELS}
SECTION_TO_FILE = {section: filename for section, _, filename in LEVELS}
CHILD_TYPES = {
    "macroarea": "area",
    "area": "sottoarea",
    "sottoarea": "concetto",
}


class EditorError(ValueError):
    """Raised for invalid editor operations."""


@dataclass(frozen=True, slots=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...]


class OntologyStore:
    """Manage an in-memory working copy of the canonical ontology."""

    def __init__(self, ontology_dir: Path, seed_path: Path | None = None) -> None:
        self.ontology_dir = ontology_dir
        self.seed_path = seed_path or (
            OUTPUT_PATH
            if ontology_dir.resolve() == OUTPUT_PATH.parent.resolve()
            else ontology_dir / "seed_compressed.py"
        )
        self._lock = RLock()
        self._records = load_canonical(ontology_dir)
        self._initial_records = copy.deepcopy(self._records)
        self._activity: list[dict[str, Any]] = []
        self._activity_sequence = 0

    def _record_activity(
        self,
        action: str,
        node_id: str | None = None,
        detail: str = "",
    ) -> None:
        self._activity_sequence += 1
        self._activity.append(
            {
                "sequence": self._activity_sequence,
                "action": action,
                "node_id": node_id,
                "detail": detail,
            }
        )
        self._activity = self._activity[-100:]

    def reload(self) -> None:
        with self._lock:
            self._records = load_canonical(self.ontology_dir)
            self._record_activity("discard", detail="Working copy reloaded")

    def _all_nodes(self) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        for section, node_type, _ in LEVELS:
            for record in self._records[section]:
                nodes.append(
                    {
                        **record,
                        "parent_id": record.get("parent_id"),
                        "type": node_type,
                    }
                )
        return nodes

    def _node_index(self) -> dict[str, dict[str, Any]]:
        return {node["id"]: node for node in self._all_nodes()}

    def _find_record(self, node_id: str) -> tuple[str, int, dict[str, Any]]:
        for section, _, _ in LEVELS:
            for index, record in enumerate(self._records[section]):
                if record["id"] == node_id:
                    return section, index, record
        raise KeyError(node_id)

    def node(self, node_id: str) -> dict[str, Any]:
        with self._lock:
            nodes = self._node_index()
            if node_id not in nodes:
                raise KeyError(node_id)
            node = nodes[node_id]
            children = [item for item in nodes.values() if item.get("parent_id") == node_id]
            descendant_ids = self._descendant_ids(node_id, nodes)
            child_type = CHILD_TYPES[node["type"]]
            return {
                **node,
                "children_count": len(children),
                "descendants_count": len(descendant_ids),
                "child_type": child_type,
                "child_creation_supported": child_type in TYPE_TO_SECTION,
                "path": self._path(node_id, nodes),
            }

    @staticmethod
    def _descendant_ids(node_id: str, nodes: dict[str, dict[str, Any]]) -> set[str]:
        descendants: set[str] = set()
        pending = [node_id]
        while pending:
            parent_id = pending.pop()
            children = [
                node["id"]
                for node in nodes.values()
                if node.get("parent_id") == parent_id and node["id"] not in descendants
            ]
            descendants.update(children)
            pending.extend(children)
        return descendants

    def _path(self, node_id: str, nodes: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
        path: list[dict[str, str]] = []
        seen: set[str] = set()
        current = nodes.get(node_id)
        while current is not None and current["id"] not in seen:
            seen.add(current["id"])
            path.append({"id": current["id"], "label": current["label"]})
            current = nodes.get(current.get("parent_id"))
        path.reverse()
        return path

    @staticmethod
    def _search_value(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", value)
        return "".join(
            character for character in decomposed if not unicodedata.combining(character)
        ).casefold()

    @staticmethod
    def _ui_sort_key(node: dict[str, Any]) -> tuple[str, str, str]:
        return (
            OntologyStore._search_value(str(node["label"])),
            OntologyStore._search_value(str(node["type"])),
            OntologyStore._search_value(str(node["id"])),
        )

    def tree(self, query: str = "") -> list[dict[str, Any]]:
        with self._lock:
            nodes = self._all_nodes()
            children: dict[str | None, list[dict[str, Any]]] = {}
            for node in nodes:
                children.setdefault(node.get("parent_id"), []).append(node)
            for siblings in children.values():
                siblings.sort(key=self._ui_sort_key)
            normalized_query = self._search_value(query.strip())

            def branch(node: dict[str, Any]) -> dict[str, Any] | None:
                child_branches = [
                    child_branch
                    for child in children.get(node["id"], [])
                    if (child_branch := branch(child)) is not None
                ]
                matches = not normalized_query or any(
                    normalized_query in self._search_value(str(node[field]))
                    for field in ("id", "label", "description")
                )
                if normalized_query and not matches and not child_branches:
                    return None
                return {
                    "id": node["id"],
                    "type": node["type"],
                    "label": node["label"],
                    "description": node["description"],
                    "match": matches,
                    "children": child_branches,
                }

            return [root for node in children.get(None, []) if (root := branch(node)) is not None]

    @staticmethod
    def _identifier_part(value: str) -> str:
        normalized = OntologyStore._search_value(value)
        return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", normalized)).strip("_")

    def suggest_id(self, parent_id: str | None, label: str) -> dict[str, Any]:
        with self._lock:
            parts = [
                part
                for part in (
                    self._identifier_part(parent_id or ""),
                    self._identifier_part(label),
                )
                if part
            ]
            suggestion = "_".join(parts)
            if not suggestion:
                raise EditorError("Cannot suggest an ID from an empty label")
            identifiers = set(self._node_index())
            collision = suggestion in identifiers
            if collision:
                suffix = 2
                while f"{suggestion}_{suffix}" in identifiers:
                    suffix += 1
                suggestion = f"{suggestion}_{suffix}"
            return {"id": suggestion, "collision": collision}

    @staticmethod
    def _canonical_record(node: dict[str, Any]) -> dict[str, Any]:
        record = {
            "id": node["id"],
            "label": node["label"],
            "description": node["description"],
            "language": node["language"],
        }
        if node["type"] != "macroarea":
            record["parent_id"] = node["parent_id"]
            return {
                "id": record["id"],
                "label": record["label"],
                "parent_id": record["parent_id"],
                "description": record["description"],
                "language": record["language"],
            }
        return record

    def create(self, node: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            if node["type"] not in TYPE_TO_SECTION:
                raise EditorError(f"Unsupported ontology type: {node['type']}")
            if node["id"] in self._node_index():
                raise EditorError(f"Duplicate ontology ID: {node['id']}")
            section = TYPE_TO_SECTION[node["type"]]
            self._records[section].append(self._canonical_record(node))
            self._record_activity("create", node["id"], node["label"])
            return self.node(node["id"])

    def update(self, node_id: str, node: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            section, index, _ = self._find_record(node_id)
            if node["type"] not in TYPE_TO_SECTION:
                raise EditorError(f"Unsupported ontology type: {node['type']}")
            existing_ids = self._node_index()
            if node["id"] != node_id and node["id"] in existing_ids:
                raise EditorError(f"Duplicate ontology ID: {node['id']}")
            if node["id"] != node_id and any(
                item.get("parent_id") == node_id for item in existing_ids.values()
            ):
                raise EditorError("Cannot change the ID of a node that has children")

            target_section = TYPE_TO_SECTION[node["type"]]
            record = self._canonical_record(node)
            if target_section == section:
                self._records[section][index] = record
            else:
                self._records[section].pop(index)
                self._records[target_section].append(record)
            self._record_activity("update", node["id"], node["label"])
            return self.node(node["id"])

    def delete(self, node_id: str) -> None:
        with self._lock:
            nodes = self._node_index()
            if any(node.get("parent_id") == node_id for node in nodes.values()):
                raise EditorError("Cannot delete a node that has children")
            section, index, _ = self._find_record(node_id)
            self._records[section].pop(index)
            self._record_activity("delete", node_id)

    def _runtime_graph(self) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]:
        validate_canonical_schema(self._records)
        nodes: dict[str, dict[str, Any]] = {}
        edges: list[dict[str, str]] = []
        for node in self._all_nodes():
            nodes[node["id"]] = node
            parent_id = node.get("parent_id")
            if parent_id is not None:
                edges.append({"source": parent_id, "target": node["id"], "relation": "CONTAINS"})
        return nodes, edges

    def validate(self) -> ValidationResult:
        with self._lock:
            try:
                nodes, edges = self._runtime_graph()
            except SeedGenerationError as exc:
                return ValidationResult(False, (str(exc),))
            errors = tuple(validate_graph(nodes, edges))
            return ValidationResult(not errors, errors)

    @staticmethod
    def _write_temp(path: Path, content: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                handle.write(content)
        except Exception:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise
        if temporary_path is None:
            raise RuntimeError(f"Failed to create temporary file for {path}")
        return temporary_path

    def save(self) -> ValidationResult:
        with self._lock:
            result = self.validate()
            if not result.valid:
                return result

            contents = {
                self.ontology_dir / SECTION_TO_FILE[section]: (
                    json.dumps(records, ensure_ascii=False, indent=2) + "\n"
                )
                for section, records in self._records.items()
            }
            contents[self.seed_path] = render_seed_module(self._records)
            temporary: dict[Path, Path] = {}
            try:
                temporary = {
                    destination: self._write_temp(destination, content)
                    for destination, content in contents.items()
                }
                for destination, source in temporary.items():
                    os.replace(source, destination)
            finally:
                for source in temporary.values():
                    source.unlink(missing_ok=True)
            self._record_activity("save", detail="Canonical ontology saved")
            return result

    def snapshot(self) -> dict[str, list[dict[str, Any]]]:
        with self._lock:
            return copy.deepcopy(self._records)

    def initial_snapshot(self) -> dict[str, list[dict[str, Any]]]:
        with self._lock:
            return copy.deepcopy(self._initial_records)

    def activity(self) -> tuple[dict[str, Any], ...]:
        with self._lock:
            return tuple(copy.deepcopy(self._activity))

    def replace_and_save(self, records: dict[str, list[dict[str, Any]]]) -> None:
        """Replace the working copy and persist it only when fully valid."""
        with self._lock:
            previous = self._records
            self._records = copy.deepcopy(records)
            result = self.save()
            if not result.valid:
                self._records = previous
                raise EditorError("\n".join(result.errors))
            self._record_activity("import", detail="Validated ontology import")
