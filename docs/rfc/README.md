# IKG Request for Comments (RFC)

This directory records significant architectural and governance decisions for the Italian Knowledge Graph project.

## Purpose

An RFC describes a proposal that affects the long-term structure, behavior, compatibility, or governance of IKG. Implementation details may evolve, but accepted architectural decisions remain traceable.

## Lifecycle

An RFC uses one of these statuses:

- **Draft** — initial proposal, still being written.
- **Review** — ready for community and maintainer feedback.
- **Accepted** — approved as an official project decision.
- **Implemented** — accepted and reflected in the repository.
- **Deprecated** — no longer authoritative; the superseding RFC must be identified.

A Draft or Review RFC may be edited. Once Accepted, its decision text is frozen. A material change requires a new RFC that explicitly supersedes or amends the previous one.

## Process

1. Copy `RFC_TEMPLATE.md`.
2. Assign the next available four-digit number.
3. Describe motivation, proposal, compatibility, alternatives, and open questions.
4. Open a pull request and request review.
5. Resolve substantive feedback before changing the status to Accepted.
6. Track implementation separately when useful.

## Index

| RFC | Title | Status |
|---|---|---|
| [RFC-0001](RFC-0001-core-architecture.md) | IKG Core Architecture | Draft Frozen |
| [RFC-0002](RFC-0002-validator-architecture.md) | IKG Validator Architecture | Draft |
| [RFC-0003](RFC-0003-validation-rule-registry.md) | Validation Rule Registry | Draft |
| [RFC-0004](RFC-0004-entity-model.md) | Entity Model | Draft |
| [RFC-0005](RFC-0005-relationship-model.md) | Relationship Model | Draft |
| [RFC-0006](RFC-0006-serialization-model.md) | Serialization Model | Draft |
| [RFC-0007](RFC-0007-validator-implementation.md) | Validator Implementation | Draft |

## Architecture sequence

```text
RFC-0001  Core Architecture
    ↓
RFC-0002  Validator Architecture
    ↓
RFC-0003  Validation Rule Registry
    ↓
RFC-0004  Entity Model
    ↓
RFC-0005  Relationship Model
    ↓
RFC-0006  Serialization Model
    ↓
RFC-0007  Validator Implementation
```

Together, RFC-0004, RFC-0005, and RFC-0006 define the initial logical and physical metamodel of IKG. RFC-0007 translates the validation contracts into a shared reference implementation boundary.

## Planned sequence

- RFC-0008 — Dataset Generator
- RFC-0009 — AI Reviewer

## Guiding principle

> **AI proposes. Software verifies. The community decides.**
