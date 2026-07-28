# Italian Knowledge Graph

An open-source project for building a structured, reusable knowledge graph in Italian.

The project models knowledge through a hierarchical structure:

```text
Macroarea
  └── Area
      └── Sottoarea
          └── Concetto
```

The knowledge graph is intended to serve as a stable source from which multiple downstream artifacts can be generated, including JSONL datasets, RAG knowledge bases, fine-tuning datasets, CSV, SQLite, GraphML, RDF/OWL and Neo4j imports.

## Current seed

The first imported seed contains:

- 48 macroareas
- 471 areas
- 710 subareas
- 1,229 total nodes
- 1,181 hierarchical `CONTAINS` edges

The original generated material is preserved losslessly in `ontology/seed_compressed.py`. It is a temporary compatibility layer while the data is progressively reorganized into human-readable modules by domain.

## Quick start

Requires Python 3.10 or later.

Validate the ontology:

```bash
python -m validators.validate_ontology
```

Export nodes and edges to JSONL:

```bash
python -m exporters.export_jsonl --output-dir datasets
```

Run tests:

```bash
python -m pytest
```

## Current status

- [x] Repository foundation
- [x] Complete initial ontology seed imported
- [x] Macroareas defined
- [x] Areas defined
- [x] Subareas defined
- [ ] Concepts
- [ ] Semantic cross-relations
- [x] Initial structural validator
- [x] Initial JSONL exporter
- [ ] Additional exporters
- [ ] Dataset generator
- [ ] Public release

## Project principles

- The ontology is the source of truth.
- Generated datasets are derived artifacts.
- Node identifiers must remain stable over time.
- Every node should be machine-readable and human-reviewable.
- Contributions should preserve structural consistency and traceability.

## Repository structure

```text
italian-knowledge-graph/
├── docs/
├── ontology/
│   ├── build.py
│   ├── macroareas.py
│   ├── areas.py
│   ├── subareas.py
│   └── seed_compressed.py
├── exporters/
│   └── export_jsonl.py
├── validators/
│   └── validate_ontology.py
├── tests/
│   └── test_ontology.py
├── README.md
├── ROADMAP.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── LICENSE
└── .gitignore
```

## Status notice

This repository is currently private and under active development. The ontology is not yet considered complete or authoritative.

## License

Licensed under the Apache License 2.0. See `LICENSE` for details.
