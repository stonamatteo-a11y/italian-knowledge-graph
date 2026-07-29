# Architecture

The ontology is the source of truth. Exported datasets and databases are derived artifacts and must never be edited manually.

## Layers

```text
Ontology seed and domain modules
        ↓
Graph builder
        ↓
Validators
        ↓
Exporters
        ↓
JSONL / CSV / SQLite / GraphML / Neo4j
```

## Current hierarchy

```text
Macroarea → Area → Sottoarea → Concetto
```

The `Concetto` level is planned and not yet populated.

## Stability rules

1. Node IDs are permanent once published.
2. A node has one hierarchical parent.
3. Cross-domain links use semantic edges rather than duplicate nodes.
4. Every parent reference must resolve to an existing node.
5. Generated files belong in `datasets/` and should be reproducible.

## Ontology source

The canonical ontology is stored as ordered, human-readable records in:

- `ontology/macroareas.json`
- `ontology/areas.json`
- `ontology/subareas.json`

`ontology/legacy_ontology_source.py` is the recovered original source retained
for migration provenance. It is not a runtime or canonical data source.

`ontology/seed_compressed.py` is a generated compatibility artifact consumed by
the existing graph builder and domain modules. Regenerate it after an approved
canonical ontology change:

```bash
python scripts/generate_seed.py
```

Never edit the compressed seed directly. CI regenerates it and rejects any
difference from the committed artifact. Ontology changes must update the
canonical JSON, preserve stable identifiers, pass review, and pass the
authoritative deterministic Validator.
