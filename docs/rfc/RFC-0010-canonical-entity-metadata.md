# RFC-0010 — Canonical Entity Metadata

**Status:** Draft
**Author:** Italian Knowledge Graph Project
**Created:** 2026-07-31
**Depends on:** RFC-0004, RFC-0005, RFC-0006
**Supersedes:** None

---

## Abstract

This RFC proposes the canonical serialization of optional aliases, sources,
notes, and semantic relationship references collected by the Ontology Editor
and guided contribution workflow.

## Motivation

The guided DOCX currently collects sources, synonyms, notes, and proposed
relationships. These values must not become canonical until their representation
and validation rules are explicit, but they must not be silently discarded.

## Proposed entity properties

Canonical entity records may omit the following properties when empty:

- `aliases`: an ordered list of non-empty strings;
- `sources`: an ordered list of source objects;
- `notes`: an ordered list of non-empty strings;
- `relations`: an ordered list of embedded relationship references.

Missing properties are semantically equivalent to empty lists. Existing records
therefore require no migration rewrite.

Aliases, sources, notes, and relations are normalized and ordered
deterministically before persistence. Duplicate values are invalid or
deterministically merged during an additive contribution import.

## Source serialization

A source object may contain:

- `url`;
- `title`;
- `publisher`;
- `accessed_at`;
- `note`.

Every property is optional, but an object with no populated property is invalid.
`url` accepts a formally valid URL or URI. `accessed_at` uses ISO 8601 date or
datetime syntax.

Sources describe the entity as a whole. They do not implicitly establish
provenance for every entity property or relationship.

## Embedded relationship serialization

An embedded relation contains:

- `predicate`;
- `target_id`;
- optional `note`.

The containing entity is the relationship source. The predicate must resolve to
the governed relationship-type registry and the target must resolve to a
canonical entity. Embedded relations are projected to the first-class
Relationship Model for validation and export.

Free text is contribution material, not a canonical relationship. Ambiguous
text remains visible in Preview and blocks import until converted.

## DOCX syntax

Aliases and notes use one value per line.

Sources use one block per source, separated by an empty line or `---`. A block
uses these labels:

```text
URL/URI: https://example.org/resource
Titolo: Titolo della fonte
Editore: Nome editore
Data di accesso: 2026-07-31
Nota: Nota facoltativa
```

Legacy free-text source values are retained as the `note` of one source.

Relationship proposals use one line per relation:

```text
PREDICATE -> target_id | nota facoltativa
```

## Compatibility

The properties are optional, so existing canonical records remain valid. The
generated structural compatibility seed may omit optional metadata only where
runtime consumers explicitly document that limitation; canonical JSON and
lossless exporters must preserve it.

## Open decision: semantic relationship registry

The current implemented registry contains only `CONTAINS`. That predicate is
already represented canonically by `parent_id`; duplicating it in `relations`
would violate containment uniqueness.

No semantic predicate can therefore be admitted until its identifier,
directionality, symmetry, endpoint constraints, duplicate policy, and
self-relationship policy are approved. This RFC deliberately does not infer
those semantics from free text or from a predicate name.

## Decision

Pending review. Alias, source, and note serialization can be adopted
independently. Canonical semantic relationship admission remains blocked until
the relationship registry decision is accepted.
