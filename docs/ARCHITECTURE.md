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

## Migration plan

The complete imported seed is currently preserved in `ontology/seed_compressed.py`. It will be progressively split into readable domain modules without changing IDs or meaning.
