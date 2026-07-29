# Contributing

Thank you for your interest in the Italian Knowledge Graph.

The project is currently under active development. Contributions should improve the ontology while preserving consistency, traceability, and stable identifiers.

## Types of contribution

Contributions may include:

- proposing missing macroareas, areas, subareas, or concepts;
- correcting labels or descriptions;
- reporting duplicated or misplaced nodes;
- improving validation tools;
- adding exporters;
- improving documentation and tests.

## Ontology rules

Every node must contain at least:

- `id`
- `label`
- `type`
- `parent_id`
- `description`
- `language`

Allowed hierarchy:

```text
macroarea → area → sottoarea → concetto
```

Rules:

1. IDs must be unique, stable, lowercase, and use underscores.
2. A node must reference an existing parent, except for macroareas.
3. Labels and descriptions must be written in Italian.
4. Descriptions should be concise, neutral, and unambiguous.
5. Do not rename an existing ID without documenting a migration.
6. Cross-domain links must be represented as semantic relations, not by duplicating nodes.
7. Generated files must not be edited manually when a source file exists.

## Canonical ontology data

Ontology records are maintained in `ontology/macroareas.json`,
`ontology/areas.json`, and `ontology/subareas.json`. Preserve record ordering,
labels, descriptions, parent relationships, and stable identifiers unless the
change is explicitly proposed and reviewed.

After changing canonical ontology data, regenerate the runtime compatibility
seed:

```bash
python scripts/generate_seed.py
```

Do not edit `ontology/seed_compressed.py` directly. It is deterministic generated
output, and CI verifies that it matches the canonical JSON. The recovered
`ontology/legacy_ontology_source.py` remains in the repository solely as
migration provenance.

Generation does not validate the meaning or quality of ontology changes. The
deterministic Validator remains authoritative.

## Proposed workflow

1. Open an issue describing the change.
2. Create a focused branch.
3. Modify the ontology source or tooling.
4. Run validators and tests.
5. Open a pull request with a clear explanation.

## Commit messages

Use concise conventional-style messages when practical:

```text
feat: add concept schema
fix: remove orphan subarea
validate: detect duplicate node IDs
docs: clarify ontology conventions
```

## Pull requests

A pull request should explain:

- what changed;
- why the change is needed;
- which ontology nodes are affected;
- whether identifiers or generated artifacts change;
- how the change was validated.

## Content quality

The ontology is not intended to encode personal opinions or promotional claims. Contested subjects should be described neutrally and, where appropriate, include provenance and multiple recognized perspectives.
