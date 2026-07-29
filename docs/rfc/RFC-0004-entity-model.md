# RFC-0004 — Entity Model

**Status:** Draft  
**Author:** Italian Knowledge Graph Project  
**Created:** 2026-07-29  
**Depends on:** RFC-0001, RFC-0002, RFC-0003  
**Supersedes:** None

---

## Abstract

This RFC defines the logical model of an IKG Entity. An Entity is the canonical unit of identity in the Italian Knowledge Graph. The RFC specifies identity, type, state, hierarchy participation, lifecycle, and model invariants without prescribing JSON, RDF, a graph database, or any other physical representation.

## Motivation

The Validator, exporters, dataset generators, and future applications require a shared definition of the objects they consume. That definition must exist independently of storage formats and implementation languages.

Without a stable entity model, serialization details may silently become the data model. IKG instead defines the logical contract first and maps physical representations to it later.

## Scope

This RFC defines:

- what an Entity is;
- the distinction between identity and mutable state;
- the initial canonical entity types;
- the primary containment hierarchy;
- the lifecycle of proposed and canonical entities;
- model invariants that every conforming implementation must preserve.

This RFC does not define semantic relationships or serialization formats.

## Entity definition

An **Entity** represents one identifiable unit of knowledge in IKG.

An Entity:

- has one stable identity;
- has one canonical type;
- has a human-readable label;
- may contain additional descriptive properties;
- may participate in relationships;
- may occupy one position in the primary containment hierarchy.

The same real-world or abstract subject must not be represented by multiple canonical Entities merely because its label, description, source, or presentation changes.

## Identity and state

Entity identity and Entity state are distinct.

### Identity

Identity is represented by a stable identifier. Once an identifier is assigned to a canonical Entity, it is treated as a public contract.

An identifier:

- is globally unique within IKG;
- is not changed when the Entity label, description, parent, or metadata changes;
- is not reassigned to a different Entity;
- remains reserved after deprecation or removal.

### State

State consists of the properties that describe the Entity at a given repository revision. State may evolve through reviewed contributions without changing identity.

Examples of mutable state include:

- label;
- description;
- primary parent;
- provenance metadata;
- aliases;
- lifecycle status.

The exact physical fields used to represent state are defined by the Serialization Model.

## Canonical entity types

Version 0.1 defines four canonical entity types:

```text
Macroarea
    ↓
Area
    ↓
Sottoarea
    ↓
Concetto
```

These types form the initial organizational backbone of IKG.

A new canonical entity type requires a dedicated RFC because it affects validation, hierarchy, serialization, contribution workflows, and downstream consumers.

## Minimum logical properties

Every canonical Entity has, at minimum:

- **Identifier** — stable public identity;
- **Type** — one canonical entity type;
- **Label** — primary human-readable name.

Every non-root Entity also has:

- **Primary parent** — the Entity that contains it in the canonical hierarchy.

A description may be present and is expected for knowledge-rich layers, but this RFC does not make it universally mandatory. Content requirements may be tightened by a later RFC without changing Entity identity.

## Primary containment hierarchy

The primary hierarchy is a classification structure, not a general semantic relation.

The permitted parent mapping in version 0.1 is:

| Entity type | Permitted primary parent |
|---|---|
| Macroarea | None |
| Area | Macroarea |
| Sottoarea | Area |
| Concetto | Sottoarea |

Each non-root Entity has exactly one primary parent. An Entity may have many semantic relationships, but those relationships do not create additional primary parents.

## Entity lifecycle

IKG distinguishes proposals from canonical knowledge.

A proposed Entity may exist in contribution material, working files, issues, or AI-assisted review output. It becomes canonical only after:

1. deterministic validation;
2. human review;
3. merge into the canonical repository state.

Only canonical Entities are part of the authoritative Knowledge Graph.

AI-generated or AI-suggested Entities have no special status and follow the same contribution lifecycle as human proposals.

## Model invariants

The following invariants define the Entity Model.

### ENT-INV-001 — Unique identity

Each canonical Entity has exactly one identifier, and no two canonical Entities share that identifier.

### ENT-INV-002 — Stable identity

An established identifier is not reassigned or silently replaced.

### ENT-INV-003 — Single canonical type

Each canonical Entity has exactly one canonical entity type.

### ENT-INV-004 — Required label

Each canonical Entity has one non-empty primary label.

### ENT-INV-005 — Single primary parent

Each non-root Entity has exactly one primary parent. A Macroarea has no primary parent.

### ENT-INV-006 — Valid parent type

The primary parent type follows the permitted parent mapping defined by this RFC.

### ENT-INV-007 — Reachability

Every non-root canonical Entity is reachable from exactly one Macroarea by following primary-parent links.

### ENT-INV-008 — Acyclic hierarchy

The primary containment hierarchy contains no cycles.

### ENT-INV-009 — Semantic independence

Semantic relationships do not alter Entity identity, canonical type, or primary-parent membership.

### ENT-INV-010 — Canonical admission

A proposed Entity is not canonical until it has passed deterministic validation and human review and has entered the canonical repository state.

## Extensibility

Implementations may carry additional properties provided that they:

- preserve the invariants in this RFC;
- do not redefine identity;
- do not create competing primary hierarchies;
- remain explicitly documented;
- do not become canonical requirements without an RFC.

## Compatibility

The following changes are compatibility-sensitive:

- identifier reassignment;
- changing the meaning of an existing entity type;
- changing permitted parent mappings;
- introducing multiple primary parents;
- changing the canonical admission lifecycle.

Such changes require a new RFC with migration guidance.

## Alternatives considered

### Serialization-first model

Rejected because JSON keys, database columns, or RDF predicates would become accidental architectural commitments.

### Multiple primary parents

Rejected for version 0.1 because it would make canonical classification ambiguous. Cross-domain structure belongs in semantic relationships.

### Mandatory rich metadata for all Entities

Rejected for version 0.1 to keep the canonical core minimal and allow gradual enrichment.

## Decision

IKG adopts a technology-independent Entity Model based on stable identity, one canonical type, one primary label, and one primary containment path. Semantic relationships and physical representations are defined separately.