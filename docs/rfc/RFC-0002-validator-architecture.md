# RFC-0002 — IKG Validator Architecture

**Status:** Draft  
**Author:** Italian Knowledge Graph Project  
**Created:** 2026-07-29  
**Depends on:** RFC-0001 — IKG Core Architecture  
**Supersedes:** None

---

## Abstract

This RFC defines the architecture and public behavior of the IKG Validator. The Validator is the deterministic software component responsible for checking whether a Knowledge Graph conforms to the objective rules adopted by the project.

The Validator does not modify canonical knowledge and does not decide semantic or scientific truth.

## Objectives

The Validator must provide:

- deterministic and reproducible results;
- structural and referential integrity checks;
- stable machine-readable outcomes;
- a reusable validation API;
- a stable command-line interface;
- compatibility with automated continuous-integration workflows.

For the same Validator version, rule registry, configuration, and input graph, the result must be identical.

## Authority and boundaries

The Validator is authoritative only for deterministic project rules.

It may verify:

- schema conformance;
- identifier constraints;
- canonical hierarchy constraints;
- parent and reference integrity;
- supported relation constraints;
- graph-level structural invariants.

It does not verify:

- scientific correctness;
- completeness of human knowledge;
- writing quality;
- semantic usefulness;
- whether a concept should exist;
- whether an AI suggestion should be accepted.

Those judgments remain subject to human governance. An AI Reviewer may provide non-binding semantic suggestions but must remain separate from the Validator.

## Core principles

### Determinism

The Validator must not depend on probabilistic models, remote AI services, or nondeterministic decision procedures.

### Offline operation

Canonical validation must be executable without network access.

### Read-only behavior

Validation must not rewrite, repair, normalize, or otherwise modify the canonical graph automatically.

### Stable ordering

Rules, findings, and report entries must be processed and emitted in a stable order so that independent runs can be compared reliably.

### Separation of interface and engine

The command-line interface is a frontend to a reusable validation API and engine. Other integrations, including continuous integration, Python applications, and future services, must be able to invoke the same engine without duplicating validation logic.

### Independent rules

Each validation rule represents one objective constraint and can be executed independently through a common rule interface.

## Logical architecture

```text
Command-line interface and integrations
                ↓
         Validation API
                ↓
        Validation engine
                ↓
     Registered validation rules
                ↓
        Immutable report
```

The implementation language and internal module layout are not mandated by this RFC.

## Validation domains

The Validator supports the following validation domains:

1. Schema
2. Identifiers
3. Hierarchy
4. Relations
5. Integrity

The official rules and their identifiers are defined by RFC-0003 and its associated Rule Registry.

## Findings

Every finding contains at least:

- a permanent Rule ID;
- a severity;
- a concise message;
- sufficient location or entity context to identify the violation.

The official severities are:

- **ERROR** — the graph is invalid;
- **WARNING** — the graph remains valid but contains a documented anomaly;
- **INFO** — non-blocking diagnostic information.

## Validation report

Every complete validation produces an immutable report containing at least:

- Validator version;
- validation result;
- number of errors;
- number of warnings;
- number of informational findings;
- ordered findings;
- principal graph statistics.

The report is descriptive and must not modify the graph.

At minimum, the system must support:

- a human-readable representation;
- a deterministic structured representation for automation.

## Command-line interface

Version 0.1 exposes the following public commands:

### `ikg validate`

Runs complete validation and emits a report and exit code.

### `ikg stats`

Displays deterministic graph statistics, including node and relation counts and distribution by canonical node type.

### `ikg doctor`

Checks whether the local project configuration and required inputs are available and suitable for validation.

## Exit codes

The public exit codes are:

| Code | Meaning |
|---:|---|
| 0 | Validation completed without errors |
| 1 | Validation rule errors were found |
| 2 | Internal Validator failure |
| 3 | Invalid configuration or unusable input |

Exit-code meaning is compatibility-sensitive and must not change silently.

## Continuous integration

The Validator is designed to run on every proposed canonical graph change.

A validation result containing one or more ERROR findings must fail the validation job and prevent automatic integration where branch protection is enabled.

The specific CI provider and workflow configuration are implementation details outside this RFC.

## Version 0.1 scope

Version 0.1 includes:

- reusable validation API and engine;
- registered independent rules;
- schema validation;
- identifier validation;
- hierarchy validation;
- relation validation;
- referential and graph integrity validation;
- immutable reports;
- `validate`, `stats`, and `doctor` commands;
- stable exit behavior.

## Non-goals

This RFC does not define:

- the complete node data model;
- the complete relation vocabulary;
- the individual Rule IDs and rule definitions;
- a specific file format;
- automatic graph repair;
- semantic review by AI;
- a remote validation service.

## Compatibility

The following are public compatibility commitments:

- command names;
- exit-code meaning;
- Rule ID meaning;
- severity meaning;
- deterministic report semantics.

Material changes require an explicit RFC and, where necessary, migration guidance.

## Decision state

This RFC is a **Draft**. It defines the proposed architecture and public contract of the IKG Validator and is ready for consistency review against RFC-0001 and RFC-0003.