# Italian Knowledge Graph

An open-source project for building a structured, reusable knowledge graph in Italian.

The project models knowledge through a hierarchical structure:

```text
Macroarea
  └── Area
      └── Sottoarea
          └── Concetto
```

The knowledge graph is intended to serve as a stable source from which multiple downstream artifacts can be generated, including:

- JSONL datasets
- RAG knowledge bases
- fine-tuning datasets
- CSV exports
- SQLite databases
- GraphML graphs
- RDF/OWL resources
- Neo4j imports

## Current status

- [x] Repository foundation
- [x] Initial ontology source available
- [x] Macroareas defined
- [x] Areas defined
- [x] Subareas partially defined
- [ ] Concepts
- [ ] Semantic cross-relations
- [ ] Validators
- [ ] Exporters
- [ ] Dataset generator
- [ ] Public release

## Project principles

- The ontology is the source of truth.
- Generated datasets are derived artifacts.
- Node identifiers must remain stable over time.
- Every node should be machine-readable and human-reviewable.
- Contributions should preserve structural consistency and traceability.

## Planned repository structure

```text
italian-knowledge-graph/
├── docs/
├── ontology/
├── exporters/
├── validators/
├── tests/
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
