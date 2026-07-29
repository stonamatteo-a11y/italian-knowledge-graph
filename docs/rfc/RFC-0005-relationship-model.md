# RFC-0005 — Relationship Model

**Status:** Draft  
**Author:** Italian Knowledge Graph Project  
**Created:** 2026-07-29  
**Depends on:** RFC-0001, RFC-0004  
**Supersedes:** None

---

## Abstract

This RFC defines the logical model of an IKG Relationship. A Relationship connects two canonical Entities and expresses either canonical containment or a documented semantic association. The RFC defines identity, direction, endpoints, type, properties, lifecycle, and invariants without prescribing a storage technology.

## Motivation

A Knowledge Graph is not only a collection of Entities. Its value depends on explicit, reviewable, and machine-processable connections between them.

Relationships must therefore be governed as first-class logical objects rather than inferred from labels, file layout, or database-specific edges.

## Scope

This RFC defines:

- what a Relationship is;
- source, target, type, and direction;
- the distinction between containment and semantic relationships;
- relationship identity and properties;
- lifecycle and model invariants.

This RFC does not define the complete vocabulary of semantic relationship types. That vocabulary may evolve through dedicated RFCs or governed registries.

## Relationship definition

A **Relationship** is a typed connection from one canonical Entity to another canonical Entity.

Every canonical Relationship has:

- a source Entity;
- a target Entity;
- one relationship type;
- a defined direction;
- a canonical status.

A Relationship may also have descriptive or provenance properties.

## Relationship classes

IKG distinguishes two logical classes.

### Primary containment

Primary containment represents the canonical hierarchy defined by RFC-0004.

Its logical meaning is:

```text
parent CONTAINS child
```

Primary containment:

- is directional;
- determines canonical hierarchy membership;
- is constrained by entity type;
- must remain acyclic;
- gives each non-root Entity exactly one primary parent.

The inverse view, such as `child IS_CONTAINED_IN parent`, may be derived and does not create a second canonical Relationship.

### Semantic relationship

A semantic Relationship expresses meaning beyond primary classification.

Examples may include prerequisite, similarity, historical influence, equivalence, application, opposition, or association. These examples are illustrative only and do not establish an official vocabulary.

Semantic Relationships:

- do not change the primary parent of an Entity;
- may cross Macroareas and hierarchy levels;
- may be directional or symmetric according to their type definition;
- must use a documented relationship type;
- are subject to human review.

## Relationship type

Each canonical Relationship uses exactly one registered type.

A relationship type definition must specify at least:

- stable type identifier;
- human-readable name;
- semantic meaning;
- directionality;
- whether it is symmetric;
- permitted source and target types, when constrained;
- duplicate policy;
- inverse behavior, when applicable.

A type must not be introduced merely as an undocumented free-text label.

## Directionality

Direction is part of relationship meaning.

For a directional type, `(A, type, B)` is not equivalent to `(B, type, A)` unless the type definition explicitly declares an inverse.

For a symmetric type, the two endpoint orders represent the same logical Relationship. A conforming implementation must normalize or detect duplicate symmetric pairs deterministically.

## Relationship identity

A canonical Relationship must be identifiable deterministically.

Its logical identity is derived from, or stably associated with:

- source Entity identifier;
- relationship type identifier;
- target Entity identifier;
- any additional discriminator explicitly required by the type definition.

The Serialization Model determines whether this identity is stored as an explicit relationship identifier or derived from canonical fields.

## Relationship properties

A Relationship may include properties such as:

- description or rationale;
- provenance;
- source references;
- review status;
- temporal scope;
- confidence supplied by a non-canonical review process.

Optional properties do not alter the semantic meaning of a registered relationship type unless that type definition explicitly says otherwise.

Probabilistic confidence must not determine canonical validity.

## Relationship lifecycle

A proposed Relationship becomes canonical only after:

1. both endpoints resolve to canonical Entities;
2. deterministic validation succeeds;
3. human review confirms the semantic proposal;
4. the Relationship enters the canonical repository state.

AI-generated suggestions remain proposals and cannot become canonical automatically.

## Model invariants

### REL-INV-001 — Existing source

The source of every canonical Relationship resolves to one canonical Entity.

### REL-INV-002 — Existing target

The target of every canonical Relationship resolves to one canonical Entity.

### REL-INV-003 — Registered type

Every canonical Relationship uses one documented and accepted relationship type.

### REL-INV-004 — Defined direction

Every relationship type has explicit directional or symmetric semantics.

### REL-INV-005 — No duplicate logical edge

The canonical graph does not contain duplicate Relationships with the same logical identity.

### REL-INV-006 — Endpoint compatibility

Source and target entity types satisfy any constraints declared by the relationship type.

### REL-INV-007 — Containment independence

A semantic Relationship does not create, replace, or imply a primary containment parent.

### REL-INV-008 — Canonical containment uniqueness

Each primary containment edge corresponds to the single primary parent defined for the child Entity.

### REL-INV-009 — Acyclic containment

Primary containment Relationships do not form cycles.

### REL-INV-010 — Canonical admission

A proposed Relationship is not canonical until deterministic validation, human review, and repository admission are complete.

## Duplicate handling

Duplicate detection depends on relationship semantics.

- For directional types, source, type, and target are ordered.
- For symmetric types, endpoint order is normalized.
- Multiple Relationships between the same endpoints are allowed only when their registered types or explicit discriminators differ.

A Relationship must not be duplicated solely to store alternate wording or provenance. Such information belongs in Relationship properties.

## Extensibility

New relationship types may be introduced through an accepted governance process. They must not modify the meaning of existing types.

A new type must define enough semantics for deterministic validation. Ambiguous or purely conversational labels are not suitable canonical types.

## Compatibility

The following changes are compatibility-sensitive:

- changing the meaning or directionality of an accepted type;
- changing a symmetric type into a directional type or vice versa;
- changing endpoint constraints;
- reusing a deprecated type identifier;
- converting a semantic type into primary containment.

Material changes require a new RFC and migration guidance.

## Alternatives considered

### Untyped edges

Rejected because they cannot be validated or interpreted consistently.

### Free-text relationship types

Rejected because spelling variants and undocumented semantics would fragment the graph.

### Treating parent fields and containment edges as independent truths

Rejected because it would create competing canonical representations. A serialization may expose one or both views, but they must represent the same logical containment fact.

## Decision

IKG adopts typed, directed, first-class Relationships between canonical Entities. Primary containment and semantic associations are logically distinct. Relationship vocabularies remain governed, deterministic, and independent of physical storage.