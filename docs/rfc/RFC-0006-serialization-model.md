# RFC-0006 — Serialization Model

**Status:** Draft  
**Author:** Italian Knowledge Graph Project  
**Created:** 2026-07-29  
**Depends on:** RFC-0001, RFC-0004, RFC-0005  
**Supersedes:** None

---

## Abstract

This RFC defines how the logical IKG Entity and Relationship models are represented in physical formats. It establishes canonical-source requirements, format independence, deterministic serialization, lossless round-tripping, version declaration, and separation between canonical and derived artifacts.

## Motivation

IKG may be consumed as JSON, YAML, CSV, SQLite, RDF, GraphML, Neo4j-oriented imports, or other formats. These representations must remain projections of one logical graph rather than competing sources of truth.

A serialization contract is therefore required before implementation of the Validator, exporters, and importers.

## Scope

This RFC defines:

- the role of canonical serialization;
- requirements shared by all supported formats;
- deterministic ordering and encoding;
- logical-to-physical mapping obligations;
- round-trip expectations;
- schema version declaration;
- canonical and derived artifact boundaries.

This RFC does not choose a graph database or require every format to support every optional property.

## Logical model precedence

RFC-0004 and RFC-0005 define the logical model.

A serialization is conforming only when it preserves that model. Storage limitations, convenience fields, or database conventions do not redefine Entity or Relationship semantics.

When a physical representation conflicts with the logical model, the logical model is authoritative.

## Canonical source and derived artifacts

IKG distinguishes:

- **canonical source serialization** — the repository representation reviewed and maintained as authoritative;
- **derived serialization** — a reproducible export generated from the canonical source.

Only one repository representation may be designated as the canonical source for a given release line.

Derived JSONL, CSV, SQLite, RDF, GraphML, Neo4j imports, indexes, and datasets must not silently become competing canonical sources.

The initial canonical source format may be selected by implementation documentation. Changing it requires an RFC and a migration plan.

## Serialization document requirements

Every canonical serialization set must make the following information available:

- serialization schema version;
- collection of Entities;
- collection of Relationships;
- canonical Entity identifiers;
- canonical Entity types and labels;
- primary containment representation;
- relationship type identifiers;
- source and target Entity references.

The information may be stored in one file or multiple files, provided the complete graph can be reconstructed deterministically.

## Entity mapping

Every serialized Entity must preserve at least:

- stable identifier;
- canonical type;
- primary label;
- primary parent reference when applicable.

Optional logical properties must retain documented meaning across supported lossless formats.

A serializer must not generate a new Entity identifier merely because the output format changes.

## Relationship mapping

Every serialized Relationship must preserve at least:

- source Entity identifier;
- relationship type identifier;
- target Entity identifier;
- any discriminator required for logical identity.

A serializer may materialize inverse or convenience edges only when they are clearly marked as derived and cannot be confused with additional canonical Relationships.

Primary containment may be represented as an Entity parent reference, a `CONTAINS` edge, or both. When both are present, they must express the same logical fact.

## Schema version

Every canonical serialization declares a schema version.

The schema version identifies the physical contract, not the release version of the knowledge content and not the version of an individual Entity.

A schema-version change is required when a consumer may need different parsing or interpretation logic.

Content additions that preserve the physical contract do not require a schema-version change.

## Determinism

Serialization must be deterministic.

Given the same canonical graph, schema version, serializer version, and configuration, a conforming serializer produces semantically identical output.

For text-based canonical formats, deterministic behavior includes:

- stable Entity ordering;
- stable Relationship ordering;
- stable property ordering where the format exposes order;
- normalized text encoding;
- normalized line endings;
- no uncontrolled timestamps, random values, or machine-specific paths.

Byte-for-byte reproducibility is required for canonical repository serialization and should be provided for derived deterministic formats where practical.

## Ordering

Physical ordering does not carry graph semantics.

A canonical serializer nevertheless defines stable ordering to support:

- reproducible builds;
- readable diffs;
- deterministic reports;
- reliable testing.

The default logical ordering is:

1. Entities by stable identifier;
2. Relationships by source identifier, relationship type identifier, target identifier, and discriminator.

A format-specific RFC may define another deterministic ordering when necessary.

## Encoding and text normalization

Text-based canonical formats use UTF-8.

Serializers must preserve Italian characters without transliteration. Unicode normalization policy must be documented and applied consistently.

Labels and descriptions are knowledge content. Serializers must not rewrite, translate, summarize, or correct them.

## References

Entity references are expressed through stable identifiers, not labels or physical file positions.

A reference that does not resolve to a canonical Entity is invalid.

Moving an Entity between files or changing its label must not break valid references.

## Null, missing, and empty values

A serialization specification must distinguish:

- a property that is absent;
- a property explicitly carrying no value, when supported;
- an empty string or empty collection.

These states must not be treated as interchangeable unless the property definition explicitly declares them equivalent.

Canonical serializers should omit unsupported optional values rather than invent placeholders.

## Round-trip behavior

A lossless format must support the following conceptual round trip:

```text
Logical graph
    ↓ serialize
Physical representation
    ↓ parse
Equivalent logical graph
```

Equivalent means that canonical Entity identities, types, labels, hierarchy, Relationship identities, types, endpoints, and all supported canonical properties are preserved.

Byte equality after a parse-and-reserialize cycle is required when the same canonical serializer and schema version are used.

A lossy export is permitted only when it is explicitly documented as derived and lists the information it omits or transforms.

## Import behavior

Importers do not automatically grant canonical status.

Imported data is treated as a proposal until it:

1. maps successfully to the logical model;
2. passes deterministic validation;
3. receives human review;
4. is merged into the canonical repository state.

An importer must report unmapped, discarded, or transformed information.

## Format profiles

Each supported physical format must have a documented profile specifying:

- file structure;
- schema version location;
- Entity mapping;
- Relationship mapping;
- data types;
- required and optional fields;
- ordering rules;
- normalization rules;
- lossless or lossy status;
- validation entry point.

A format is not officially supported until such a profile and corresponding tests exist.

## Serialization invariants

### SER-INV-001 — Logical fidelity

A canonical serialization preserves the Entity and Relationship models defined by RFC-0004 and RFC-0005.

### SER-INV-002 — Stable references

All graph references use stable Entity identifiers.

### SER-INV-003 — Declared schema version

Every canonical serialization declares one supported schema version.

### SER-INV-004 — Deterministic output

The same logical input and configuration produce deterministic serialized output.

### SER-INV-005 — No hidden canonical data

Canonical meaning is not stored solely in filenames, array positions, comments, database row order, or undocumented conventions.

### SER-INV-006 — Canonical-source uniqueness

A release line has one designated canonical source representation.

### SER-INV-007 — Derived-artifact traceability

A derived serialization identifies, directly or through release metadata, the canonical source revision and generation process.

### SER-INV-008 — Explicit loss

A lossy export documents all intentionally omitted or transformed logical information.

### SER-INV-009 — No content mutation

Serialization does not semantically rewrite canonical knowledge content.

### SER-INV-010 — Import review boundary

Imported content does not become canonical without validation, human review, and repository admission.

## Compatibility

The following changes are compatibility-sensitive:

- changing field meaning;
- changing reference semantics;
- changing canonical type or relationship-type encoding;
- removing previously required information;
- changing null or missing-value semantics;
- changing normalization rules;
- changing the designated canonical source format.

Breaking physical changes require a new schema version and migration guidance.

## Alternatives considered

### One mandatory universal format for all uses

Rejected because repository maintenance, graph exchange, analytics, and model training have different requirements.

### Database as source of truth

Rejected because it would couple governance and reproducibility to a specific runtime system.

### Labels as references

Rejected because labels may change and are not guaranteed to be globally unique.

### Multiple editable canonical formats

Rejected because synchronization conflicts would create competing truths.

## Decision

IKG adopts a serialization layer that is subordinate to the logical Entity and Relationship models. One canonical source representation is maintained per release line, while all other physical formats are deterministic, documented, and traceable projections of that source.