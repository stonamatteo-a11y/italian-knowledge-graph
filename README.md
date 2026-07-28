# Italian Knowledge Graph

<p align="center">
  <img src="assets/logo.svg" alt="Italian Knowledge Graph logo" width="620">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-early%20development-orange" alt="Status: early development">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-Apache--2.0-green" alt="Apache 2.0 license">
</p>

An open-source project for building a structured, reusable knowledge graph in Italian.

The project models knowledge through a hierarchical structure:

```text
Macroarea
  └── Area
      └── Sottoarea
          └── Concetto
```

The graph is intended to be a stable source from which multiple downstream artifacts can be generated: JSONL datasets, RAG knowledge bases, fine-tuning datasets, CSV, SQLite, GraphML, RDF/OWL and Neo4j imports.

## Current seed

The first imported seed contains:

- 48 macroareas
- 471 areas
- 710 subareas
- 1,229 total nodes
- 1,181 hierarchical `CONTAINS` edges

The original generated material is preserved losslessly in `ontology/seed_compressed.py`. It is a temporary compatibility layer while the data is progressively reorganized into human-readable domain modules.

## Community review

This is an early, non-authoritative ontology seed. Feedback is especially useful on:

- missing or misplaced disciplines;
- ambiguous labels and descriptions;
- duplicate or overlapping branches;
- hierarchy balance;
- stable naming and identifier conventions;
- the future `Concetto` level and semantic relations.

Use GitHub Issues for proposals and Pull Requests for reviewed changes. See `CONTRIBUTING.md`, `docs/ARCHITECTURE.md` and `docs/NODE_SCHEMA.md`.

## Quick start

Requires Python 3.10 or later.

```bash
python -m pip install -r requirements-dev.txt
python -m validators.validate_ontology
pytest
```

Export formats:

```bash
python -m exporters.export_jsonl --output-dir datasets
python -m exporters.export_csv --output-dir datasets
python -m exporters.export_sqlite --output datasets/ontology.sqlite
python -m exporters.export_graphml --output datasets/ontology.graphml
```

## Current status

- [x] Repository foundation
- [x] Complete initial ontology seed imported
- [x] Macroareas, areas and subareas defined
- [ ] Concepts
- [ ] Semantic cross-relations
- [x] Initial structural validator
- [x] JSONL, CSV, SQLite and GraphML exporters
- [x] Automated tests and GitHub Actions
- [x] Community issue and pull request templates
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
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   └── pull_request_template.md
├── assets/
│   └── logo.svg
├── docs/
├── ontology/
├── exporters/
├── validators/
├── tests/
├── CHANGELOG.md
├── CITATION.cff
├── CONTRIBUTING.md
├── pyproject.toml
└── README.md
```

## Status notice

The repository is under active development. The ontology is not yet complete or authoritative and should be treated as a community-reviewed seed.

## License

Licensed under the Apache License 2.0. See `LICENSE` for details.
