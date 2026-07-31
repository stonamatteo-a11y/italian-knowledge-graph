"""Generate the compressed ontology seed from canonical JSON sources."""

from __future__ import annotations

import argparse
import base64
import json
import textwrap
import zlib
from collections import defaultdict
from pathlib import Path
from typing import Any

from ikg.metadata import METADATA_FIELDS, MetadataError, canonical_metadata

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = ROOT / "ontology"
OUTPUT_PATH = ONTOLOGY_DIR / "seed_compressed.py"

SOURCE_FILES = {
    "macroareas": "macroareas.json",
    "areas": "areas.json",
    "subareas": "subareas.json",
}
REQUIRED_FIELDS = {
    "macroareas": ("id", "label", "description", "language"),
    "areas": ("id", "label", "parent_id", "description", "language"),
    "subareas": ("id", "label", "parent_id", "description", "language"),
}


class SeedGenerationError(ValueError):
    """Raised when canonical ontology data is invalid."""


def load_canonical(ontology_dir: Path = ONTOLOGY_DIR) -> dict[str, list[dict[str, Any]]]:
    """Load the ordered canonical ontology records."""
    loaded: dict[str, list[dict[str, Any]]] = {}
    for section, filename in SOURCE_FILES.items():
        path = ontology_dir / filename
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SeedGenerationError(f"Cannot load {path}: {exc}") from exc
        if not isinstance(value, list):
            raise SeedGenerationError(f"{path} must contain a JSON array")
        loaded[section] = value
    return loaded


def _validate_record(
    section: str,
    index: int,
    record: Any,
    seen_ids: set[str],
) -> str:
    location = f"{SOURCE_FILES[section]} record {index}"
    if not isinstance(record, dict):
        raise SeedGenerationError(f"{location} must be an object")

    expected = set(REQUIRED_FIELDS[section])
    actual = set(record)
    allowed = expected | set(METADATA_FIELDS)
    if not expected <= actual or not actual <= allowed:
        missing = sorted(expected - actual)
        unknown = sorted(actual - allowed)
        raise SeedGenerationError(
            f"{location} has invalid fields; missing={missing}, unknown={unknown}"
        )

    for field in REQUIRED_FIELDS[section]:
        value = record[field]
        if not isinstance(value, str) or not value.strip():
            raise SeedGenerationError(f"{location} field {field!r} must be a non-empty string")

    if record["language"] != "it":
        raise SeedGenerationError(f"{location} field 'language' must be 'it'")
    try:
        canonical_metadata(record)
    except MetadataError as exc:
        raise SeedGenerationError(f"{location}: {exc}") from exc

    node_id = record["id"]
    if node_id in seen_ids:
        raise SeedGenerationError(f"Duplicate ontology ID: {node_id}")
    seen_ids.add(node_id)
    return node_id


def validate_canonical_schema(
    records: dict[str, list[dict[str, Any]]],
) -> dict[str, set[str]]:
    """Validate canonical record shape and identifier uniqueness."""
    if set(records) != set(SOURCE_FILES):
        raise SeedGenerationError("Canonical data must contain macroareas, areas, and subareas")

    seen_ids: set[str] = set()
    ids_by_section: dict[str, set[str]] = {}
    for section in SOURCE_FILES:
        section_ids: set[str] = set()
        for index, record in enumerate(records[section]):
            section_ids.add(_validate_record(section, index, record, seen_ids))
        ids_by_section[section] = section_ids
    return ids_by_section


def validate_canonical(records: dict[str, list[dict[str, Any]]]) -> None:
    """Validate canonical records and their hierarchy."""
    ids_by_section = validate_canonical_schema(records)
    seen_ids = set().union(*ids_by_section.values())
    for section, filename in SOURCE_FILES.items():
        for index, record in enumerate(records[section]):
            try:
                canonical_metadata(record, seen_ids)
            except MetadataError as exc:
                raise SeedGenerationError(f"{filename} record {index}: {exc}") from exc

    parent_sections = {
        "areas": "macroareas",
        "subareas": "areas",
    }
    for section, parent_section in parent_sections.items():
        valid_parents = ids_by_section[parent_section]
        for index, record in enumerate(records[section]):
            parent_id = record["parent_id"]
            if parent_id not in seen_ids:
                raise SeedGenerationError(
                    f"{SOURCE_FILES[section]} record {index} references missing parent "
                    f"{parent_id!r}"
                )
            if parent_id not in valid_parents:
                raise SeedGenerationError(
                    f"{SOURCE_FILES[section]} record {index} has invalid hierarchy: "
                    f"{parent_id!r} is not a {parent_section[:-1]}"
                )
    types = {
        record["id"]: section.removesuffix("s")
        for section in SOURCE_FILES
        for record in records[section]
    }
    allowed_contains = {("macroarea", "area"), ("area", "subarea")}
    for section, filename in SOURCE_FILES.items():
        for index, record in enumerate(records[section]):
            for relation in record.get("relations", []):
                direction = (types[record["id"]], types[relation["target_id"]])
                if relation["predicate"] == "CONTAINS" and direction not in allowed_contains:
                    raise SeedGenerationError(
                        f"{filename} record {index} has invalid relation "
                        f"direction: {direction[0]} -> {direction[1]}"
                    )


def _group_children(
    records: list[dict[str, Any]],
) -> list[list[Any]]:
    grouped: dict[str, list[list[str]]] = defaultdict(list)
    parent_order: list[str] = []
    for record in records:
        parent_id = record["parent_id"]
        if parent_id not in grouped:
            parent_order.append(parent_id)
        grouped[parent_id].append([record["id"], record["label"], record["description"]])
    return [[parent_id, grouped[parent_id]] for parent_id in parent_order]


def build_runtime_seed(records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Build the compatibility structures consumed by the runtime."""
    validate_canonical(records)
    return {
        "macroareas": [
            [record["id"], record["label"], record["description"]]
            for record in records["macroareas"]
        ],
        "areas": _group_children(records["areas"]),
        "subareas": _group_children(records["subareas"]),
    }


def render_seed_module(records: dict[str, list[dict[str, Any]]]) -> str:
    """Render a deterministic Python compatibility module."""
    seed = build_runtime_seed(records)
    serialized = json.dumps(
        seed,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    encoded = base64.b85encode(zlib.compress(serialized, level=9)).decode("ascii")
    wrapped = "\n".join(f'    "{line}"' for line in textwrap.wrap(encoded, width=88))
    return f'''"""Generated compressed compatibility seed."""

# AUTO-GENERATED FILE
# DO NOT EDIT DIRECTLY
# Canonical sources:
# - ontology/macroareas.json
# - ontology/areas.json
# - ontology/subareas.json

from __future__ import annotations

import base64
import json
import zlib

_DATA = (
{wrapped}
)

SEED = json.loads(zlib.decompress(base64.b85decode(_DATA.encode())).decode("utf-8"))
MACROAREAS = SEED["macroareas"]
AREAS = SEED["areas"]
SUBAREAS = SEED["subareas"]
'''


def generate_seed(
    ontology_dir: Path = ONTOLOGY_DIR,
    output_path: Path = OUTPUT_PATH,
    *,
    check: bool = False,
) -> bool:
    """Generate the compatibility module, returning whether it was current."""
    rendered = render_seed_module(load_canonical(ontology_dir))
    if check:
        try:
            current = output_path.read_text(encoding="utf-8")
        except OSError:
            current = None
        if current != rendered:
            raise SeedGenerationError(
                f"{output_path} is out of date; run python scripts/generate_seed.py"
            )
        return True

    output_path.write_text(rendered, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when the generated seed differs from the committed file",
    )
    args = parser.parse_args()
    try:
        generate_seed(check=args.check)
    except SeedGenerationError as exc:
        parser.exit(1, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
