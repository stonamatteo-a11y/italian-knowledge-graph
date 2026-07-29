# RFC-0003 — Validation Rule Registry

**Status:** Draft  
**Author:** Italian Knowledge Graph Project  
**Created:** 2026-07-29  
**Depends on:** RFC-0002 — IKG Validator Architecture  
**Supersedes:** None

---

## Abstract

This RFC defines the official registry model for deterministic validation rules used by the IKG Validator.

The Rule Registry is the authoritative catalogue of rule identities, meanings, categories, severities, lifecycle states, and compatibility commitments. The Validator may enforce only rules that are formally registered.

## Motivation

Validation behavior must remain understandable and stable as the project grows. A monolithic Validator with undocumented checks would make reports difficult to interpret, compatibility difficult to preserve, and contributions difficult to review.

A formal registry separates the architecture of the Validator from the catalogue of constraints it enforces.

## Objectives

The Rule Registry provides:

- permanent and unique Rule IDs;
- one authoritative meaning for each rule;
- stable severity and category metadata;
- traceable introduction, modification, and deprecation;
- human-readable documentation;
- machine-readable metadata;
- predictable report references.

## Rule philosophy

Every rule must be:

- objective;
- deterministic;
- reproducible;
- independently executable;
- limited to one clearly defined constraint;
- expressible without semantic judgment by an AI model.

Rules should not overlap unnecessarily. When two conditions represent materially different failures, they should normally use separate Rule IDs.

## Rule record

Every registered rule contains at least:

- **Rule ID** — permanent public identifier;
- **Title** — concise human-readable name;
- **Category** — one official validation domain;
- **Severity** — ERROR, WARNING, or INFO;
- **Description** — normative meaning of the rule;
- **Status** — Draft, Accepted, or Deprecated;
- **Introduced by** — RFC or project decision that established the rule.

A rule record should also provide:

- rationale;
- valid example;
- invalid example;
- expected finding context;
- compatibility or migration notes where relevant.

## Rule identification

Rule IDs use the permanent format:

```text
IKG001
IKG002
IKG003
...
```

Rules are assigned monotonically increasing identifiers.

A Rule ID:

- identifies exactly one rule meaning;
- must never be reassigned;
- must not be reused after deprecation;
- remains visible in historical reports and documentation.

Renaming a rule title does not change its Rule ID, provided the normative meaning remains unchanged.

## Official categories

The official categories are:

- **SCHEMA**
- **IDS**
- **HIERARCHY**
- **RELATIONS**
- **INTEGRITY**

Each rule belongs to exactly one category.

A new category requires an RFC because categories are part of the public validation contract.

## Severity

The official severities are:

### ERROR

A violation makes the Knowledge Graph invalid.

### WARNING

A violation identifies a documented anomaly but does not make the graph invalid.

### INFO

The finding is diagnostic and non-blocking.

No additional severities are defined by this RFC.

The severity of an Accepted rule is compatibility-sensitive. A material severity change requires explicit review through the RFC process.

## Rule lifecycle

A rule has one of the following states:

### Draft

The rule is proposed and may change. It must not be enforced as part of canonical validation.

### Accepted

The rule is part of the official IKG validation standard and may be enforced by the Validator.

### Deprecated

The rule is retained for compatibility and historical interpretation but must not be applied to new canonical validation unless a documented compatibility mode requires it.

An Accepted or Deprecated Rule ID is never deleted from the registry.

## Registry authority

The normative rule metadata must be maintained in a canonical machine-readable registry within the repository.

Human-readable rule documentation may be generated from, or checked against, that registry. Generated documentation must not become a competing source of truth.

The storage format of the registry is an implementation decision, provided it supports deterministic parsing, reviewable changes, and preservation of the normative fields defined here.

## Rule documentation

Each Accepted rule must include at least one valid or non-applicable example and one invalid example where an invalid case is meaningful.

Rule documentation should make it possible for a contributor to understand:

- what condition is checked;
- why it matters;
- what entity or location will be reported;
- how to resolve a violation without automatic graph mutation.

## Registry management

Introducing a new rule requires:

1. assignment of the next available Rule ID;
2. a complete rule record;
3. objective test cases;
4. review of category and severity;
5. an RFC or an RFC-governed rule change process;
6. acceptance before canonical enforcement.

Changing an Accepted rule requires distinguishing between:

- **editorial clarification**, which does not alter behavior;
- **material semantic change**, which requires a new Rule ID or an explicit superseding RFC.

A rule must receive a new Rule ID when the set of inputs considered valid or invalid changes materially and compatibility cannot be preserved.

## Deterministic ordering

The registry is ordered by Rule ID.

Validator execution order may be optimized internally, but emitted findings must use deterministic ordering defined by the Validator specification. Registry order must remain stable and reviewable.

## Relationship with the Validator

RFC-0002 defines how the Validator operates.

This RFC defines how rules are identified and governed.

The Validator:

- loads or embeds the Accepted registry deterministically;
- reports the applicable Rule ID for every rule-based finding;
- must not silently enforce unregistered checks;
- must not use Draft rules in canonical validation;
- must preserve the documented meaning and severity of Accepted rules.

## Relationship with the data model

This RFC does not define the specific node, hierarchy, or relation constraints. Those constraints originate in the relevant data-model RFCs and are represented in the registry as individual validation rules.

The initial concrete Rule IDs should be assigned only after RFC-0004 defines the Knowledge Graph data model sufficiently to describe those rules without ambiguity.

## Compatibility

The following are compatibility-sensitive:

- Rule IDs;
- normative rule meaning;
- category assignment;
- severity;
- lifecycle state;
- structured report references to rules.

Deprecated identifiers remain reserved permanently.

## Non-goals

This RFC does not:

- define the complete initial list of validation rules;
- define the node schema;
- define the relation vocabulary;
- mandate YAML, JSON, TOML, or another registry format;
- define Validator implementation classes;
- authorize AI-based validity decisions;
- define automatic correction behavior.

## Decision state

This RFC is a **Draft**. It establishes the governance and compatibility model for the IKG Validation Rule Registry. Concrete Rule IDs will be introduced after the data model they validate is formally defined.