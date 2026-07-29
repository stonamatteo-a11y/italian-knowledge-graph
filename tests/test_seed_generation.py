from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import runpy
from pathlib import Path

import pytest

from ontology import build_graph
from scripts.generate_seed import (
    ONTOLOGY_DIR,
    OUTPUT_PATH,
    SeedGenerationError,
    generate_seed,
    load_canonical,
    validate_canonical,
)

EXPECTED_GRAPH_SHA256 = "54a890d84806c25a594195dbbde82b54398b1a813156ba8900887fecbb6e5748"


def _normalized_graph() -> dict[str, object]:
    nodes, edges = build_graph()
    return {"nodes": list(nodes.values()), "edges": edges}


def _graph_digest(graph: dict[str, object]) -> str:
    serialized = json.dumps(graph, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def test_canonical_json_loading() -> None:
    records = load_canonical()

    assert {section: len(values) for section, values in records.items()} == {
        "macroareas": 48,
        "areas": 471,
        "subareas": 710,
    }
    validate_canonical(records)


def test_duplicate_ids_are_rejected() -> None:
    records = copy.deepcopy(load_canonical())
    records["areas"][0]["id"] = records["macroareas"][0]["id"]

    with pytest.raises(SeedGenerationError, match="Duplicate ontology ID"):
        validate_canonical(records)


def test_missing_parent_is_rejected() -> None:
    records = copy.deepcopy(load_canonical())
    records["areas"][0]["parent_id"] = "missing"

    with pytest.raises(SeedGenerationError, match="references missing parent"):
        validate_canonical(records)


def test_invalid_hierarchy_is_rejected() -> None:
    records = copy.deepcopy(load_canonical())
    records["subareas"][0]["parent_id"] = records["macroareas"][0]["id"]

    with pytest.raises(SeedGenerationError, match="invalid hierarchy"):
        validate_canonical(records)


def test_generation_is_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first.py"
    second = tmp_path / "second.py"

    generate_seed(ONTOLOGY_DIR, first)
    generate_seed(ONTOLOGY_DIR, second)

    assert first.read_bytes() == second.read_bytes()


def test_generated_payload_decodes(tmp_path: Path) -> None:
    output = tmp_path / "seed.py"
    generate_seed(ONTOLOGY_DIR, output)

    generated = runpy.run_path(str(output))

    assert len(generated["MACROAREAS"]) == 48
    assert sum(len(children) for _, children in generated["AREAS"]) == 471
    assert sum(len(children) for _, children in generated["SUBAREAS"]) == 710


def test_runtime_matches_recovered_legacy_source() -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        recovered = runpy.run_path(str(ONTOLOGY_DIR / "legacy_ontology_source.py"))
    expected = {
        "nodes": list(recovered["nodes"].values()),
        "edges": recovered["edges"],
    }
    actual = _normalized_graph()

    assert actual == expected
    assert _graph_digest(actual) == EXPECTED_GRAPH_SHA256
    assert len(actual["nodes"]) == 1229
    assert len(actual["edges"]) == 1181


def test_committed_seed_is_current() -> None:
    assert generate_seed(ONTOLOGY_DIR, OUTPUT_PATH, check=True)
