# RFC-0007 — Validator Implementation

**Status:** Draft  
**Author:** Italian Knowledge Graph Project  
**Created:** 2026-07-29  
**Depends on:** RFC-0002, RFC-0003, RFC-0004, RFC-0005, RFC-0006  
**Supersedes:** None

---

## Abstract

This RFC defines the initial implementation contract for the IKG Validator.

The Validator is the deterministic software component that evaluates whether a serialized IKG graph conforms to the accepted entity, relationship, serialization, and validation-rule specifications.

This RFC defines implementation boundaries, package structure, execution flow, public interfaces, reporting behavior, exit codes, testing expectations, and the scope of version 0.1.

## Motivation

The earlier RFCs define what the Validator means, how validation rules are governed, and what logical model must be validated. A concrete implementation contract is now required so that the command-line interface, Python API, automated tests, and continuous-integration pipeline all use the same validation engine.

Without this separation, different entry points could produce inconsistent results or silently implement different interpretations of the project rules.

## Implementation principles

The implementation must be:

- deterministic;
- offline-capable;
- side-effect free during validation;
- independent from AI services;
- testable at rule, engine, and command-line levels;
- stable in its public behavior;
- replaceable internally without changing the accepted contract.

The same canonical input, Validator version, configuration, and rule registry must produce the same ordered findings and the same final result.

## Language and runtime

The reference implementation is written in Python.

Python is selected because the repository already uses the Python ecosystem and because it supports maintainable command-line tooling, graph processing, testing, packaging, and future integrations.

This decision does not make Python part of the logical IKG metamodel. A future implementation in another language may be conformant if it preserves the behavior defined by the relevant RFCs.

## Architectural layers

The reference implementation is divided into the following logical layers:

```text
CLI
    ↓
Public Validator API
    ↓
Validation Engine
    ↓
Rule Registry and Rule Implementations
    ↓
Immutable Validation Report
```

### Command-line interface

The CLI translates user input into calls to the public Validator API. It must not contain independent validation logic.

### Public Validator API

The public API provides a programmatic entry point for validation. The CLI, tests, automation, and future applications must use the same API rather than bypassing it.

### Validation engine

The engine coordinates loading, rule selection, deterministic execution, finding collection, ordering, and report generation.

The engine does not define the graph model or invent validation requirements. It implements the contracts established by the governing RFCs.

### Rule implementations

Each accepted validation rule is implemented as an independent unit with a permanent Rule ID from the Validation Rule Registry.

A rule must evaluate one documented constraint and return zero or more findings. It must not modify the graph, global state, another rule, or a previously produced finding.

### Validation report

The report is the immutable result of one validation execution. Once produced, it must not be modified.

## Proposed package structure

The initial package should follow this conceptual structure:

```text
ikg/
    __init__.py
    cli.py
    validator/
        __init__.py
        api.py
        engine.py
        models.py
        registry.py
        report.py
        rules/
```

Exact filenames may evolve, but the separation between CLI, API, engine, registry, rules, and report must remain clear.

Exporters, dataset generators, and the AI Reviewer remain outside the Validator package.

## Validation execution flow

A complete validation run follows this order:

```text
Input selection
    ↓
Canonical deserialization
    ↓
Input and configuration checks
    ↓
Graph construction
    ↓
Accepted-rule discovery
    ↓
Deterministic rule execution
    ↓
Finding normalization and ordering
    ↓
Report generation
    ↓
Exit-code selection
```

Failure to deserialize or construct the graph is an execution or configuration failure, not a normal graph-rule finding unless a registered rule explicitly governs that condition.

## Rule execution

Only rules with status `Accepted` in the active registry participate in canonical validation.

Rules are executed in a stable order determined by their permanent Rule IDs unless a later RFC defines an explicit dependency mechanism.

The result of one rule must not depend on nondeterministic iteration, network access, current time, random values, external AI services, or the execution side effects of another rule.

Parallel execution may be introduced only if it produces exactly the same normalized report as sequential execution.

## Findings

A finding is one observed violation or informational result produced by a rule.

Each finding must include at least:

- Rule ID;
- severity;
- stable message or message key;
- affected entity, relationship, field, or graph location when available;
- sufficient structured context to identify the problem.

Findings must be normalized and ordered deterministically. The initial ordering is:

1. severity;
2. Rule ID;
3. affected object identifier;
4. stable location or field;
5. message key or normalized message.

Human-readable wording may improve over time, but the Rule ID and structured context remain the primary machine-stable identifiers.

## Report contract

A validation report must contain at least:

- Validator version;
- active rule-registry version or fingerprint;
- validation result;
- counts for errors, warnings, and informational findings;
- ordered findings;
- graph statistics required to interpret the run;
- execution failure information when validation could not be completed.

A graph is valid when validation completes successfully and no `ERROR` finding is present.

Warnings and informational findings do not invalidate the graph.

The report may be rendered in multiple output formats, but every lossless rendering must represent the same logical report.

## Public commands

Version 0.1 exposes three public commands:

### `ikg validate`

Runs canonical validation and produces a report.

### `ikg stats`

Reports deterministic graph statistics without redefining validation rules.

### `ikg doctor`

Checks whether the local project structure, configuration, canonical files, and runtime prerequisites are sufficient to run the Validator.

`doctor` diagnoses the environment. It does not replace `validate` and does not determine whether the graph itself is valid.

## Exit codes

The version 0.1 command-line contract uses these exit codes:

| Code | Meaning |
|---:|---|
| 0 | Command completed successfully; for `validate`, no ERROR findings were produced |
| 1 | Validation completed and one or more ERROR findings were produced |
| 2 | Validator execution failed because of an internal or unexpected error |
| 3 | Input, project configuration, or command usage is invalid |

These exit codes are compatibility-sensitive public behavior.

Warnings alone must not produce exit code `1`.

## Configuration

The Validator may accept explicit configuration, but canonical validation must have documented defaults.

Configuration must not silently disable accepted ERROR rules. Any supported rule-selection mode must be explicit in the report and must not be presented as canonical validation unless all mandatory accepted rules were executed.

Environment-specific values must not alter rule meaning.

## Error isolation

An unexpected exception in a rule must not be reported as if the graph had violated that rule.

Such a failure is an execution failure and must be distinguishable from a normal validation finding.

The report or command output must identify the affected Rule ID when available, while the CLI returns the execution-failure exit code.

## Performance

Correctness, determinism, and diagnostic clarity take priority over premature optimization.

The version 0.1 implementation should support the current ontology seed comfortably on ordinary developer hardware.

Performance improvements must not alter findings, ordering, report meaning, or exit behavior.

## Testing requirements

The reference implementation must include:

- unit tests for each accepted rule;
- valid and invalid fixtures for each rule;
- engine tests covering ordering and aggregation;
- report tests covering counts and validity decisions;
- CLI tests covering commands and exit codes;
- determinism tests that repeat the same validation run;
- regression tests for previously corrected defects.

Every accepted rule must have at least one fixture that passes and one fixture that triggers the rule, unless its documented nature makes one side impossible.

A change to rule meaning requires the RFC process defined by RFC-0003, not merely a code change.

## Continuous integration

The canonical repository graph must be validated in continuous integration for pull requests and changes to the main branch.

The CI job must fail when:

- canonical validation produces an ERROR;
- the Validator crashes;
- configuration required for canonical validation is invalid;
- the Validator test suite fails.

Warnings may be displayed without blocking the pipeline unless a later RFC defines a stricter repository policy.

## Version 0.1 scope

The first implementation includes only the minimum stable foundation:

- Python package and public API;
- deterministic validation engine;
- accepted-rule registry loading;
- independent rule execution;
- immutable structured report;
- human-readable report rendering;
- `validate`, `stats`, and `doctor` commands;
- stable exit codes;
- automated tests;
- continuous-integration execution.

The first implementation should prioritize a small accepted rule set covering structural integrity, identifiers, hierarchy, references, and supported relationship types.

## Non-goals

Version 0.1 does not include:

- AI-assisted semantic review;
- automatic graph correction;
- probabilistic validation;
- network-dependent validation;
- scientific truth assessment;
- description-quality scoring;
- automatic ID rewriting;
- graph editing through the Validator;
- export or dataset-generation logic;
- a hosted validation service.

## Compatibility

The following implementation behaviors are compatibility-sensitive:

- public command names;
- Validator API semantics;
- Rule IDs and rule meaning;
- severity meaning;
- report validity decision;
- deterministic finding order;
- exit codes.

Internal module names and implementation techniques may evolve when they do not alter these contracts.

## Security and trust

Validation must not execute code embedded in graph data.

Input parsing must treat graph content as data. Implementations should avoid unsafe deserialization and should fail clearly when resource or input limits prevent safe processing.

The Validator must not transmit canonical graph data to external services during validation.

## Alternatives considered

### Validation logic only in the CLI

Rejected because it would prevent reuse and encourage different behavior across integrations.

### Monolithic validator function

Rejected because independent rules are easier to test, govern, document, deprecate, and extend.

### AI-assisted validation

Rejected for canonical validity decisions because probabilistic output would violate determinism, reproducibility, and offline operation.

### Automatic correction

Rejected because validation and mutation have different authority and audit requirements.

## Open questions

The following details may be finalized during implementation without changing the core decision, provided public behavior remains compatible:

- the exact Python packaging tool;
- the exact internal model classes;
- the first structured report serialization;
- the initial set of accepted Rule IDs;
- optional performance instrumentation.

## Decision

IKG will implement one deterministic Python validation engine shared by the CLI, programmatic API, tests, and continuous integration.

Validation rules remain independent, registry-governed, side-effect free, and identified by permanent Rule IDs. Validation produces an immutable, deterministically ordered report and never modifies the canonical graph.
