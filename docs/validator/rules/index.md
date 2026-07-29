# IKG Validation Rule Registry

This directory contains the canonical human-readable documentation for IKG validation and runtime diagnostic identifiers.

Rule identifiers are permanent and must never be reassigned.

## Identifier ranges

| Range | Category |
|---|---|
| IKG000–IKG099 | Schema |
| IKG100–IKG199 | Identity |
| IKG200–IKG299 | Hierarchy |
| IKG300–IKG399 | Relationships |
| IKG400–IKG499 | Integrity |
| IKG900–IKG999 | Runtime diagnostics |

## Rules

### Schema

- [IKG001](IKG001.md) — Missing Required Property
- [IKG002](IKG002.md) — Invalid Property Type
- [IKG003](IKG003.md) — Unknown Property
- [IKG004](IKG004.md) — Invalid Entity Type

### Identity

- [IKG100](IKG100.md) — Duplicate Identifier
- [IKG101](IKG101.md) — Invalid Identifier Format
- [IKG102](IKG102.md) — Reserved Identifier
- [IKG103](IKG103.md) — Deprecated Identifier

### Hierarchy

- [IKG200](IKG200.md) — Missing Parent
- [IKG201](IKG201.md) — Invalid Parent Type
- [IKG202](IKG202.md) — Multiple Parents
- [IKG203](IKG203.md) — Hierarchy Cycle
- [IKG204](IKG204.md) — Orphan Entity
- [IKG205](IKG205.md) — Invalid Hierarchy Level

### Relationships

- [IKG300](IKG300.md) — Unknown Relationship Type
- [IKG301](IKG301.md) — Missing Target Entity
- [IKG302](IKG302.md) — Missing Source Entity
- [IKG303](IKG303.md) — Duplicate Relationship
- [IKG304](IKG304.md) — Self Relationship Not Allowed
- [IKG305](IKG305.md) — Invalid Relationship Direction

### Integrity

- [IKG400](IKG400.md) — Broken Reference
- [IKG401](IKG401.md) — Canonical Entity Missing
- [IKG402](IKG402.md) — Serialization Inconsistency
- [IKG403](IKG403.md) — Non-deterministic Ordering

### Runtime diagnostics

Runtime identifiers describe validator execution failures rather than graph validity findings.

- [IKG900](IKG900.md) — Internal Validator Error
- [IKG901](IKG901.md) — Configuration Error
- [IKG902](IKG902.md) — Unsupported Format
- [IKG903](IKG903.md) — Plugin Loading Failure
