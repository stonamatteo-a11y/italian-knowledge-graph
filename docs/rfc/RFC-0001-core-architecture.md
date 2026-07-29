# RFC-0001 — IKG Core Architecture

**Status:** Draft Frozen  
**Author:** Italian Knowledge Graph Project  
**Created:** 2026-07-29  
**Depends on:** None  
**Supersedes:** None

---

## Abstract

Italian Knowledge Graph (IKG) is an open-source project for building a structured knowledge base in the Italian language. IKG is not primarily a dataset or a language model. Its central asset is a governed ontology and Knowledge Graph from which datasets, retrieval systems, benchmarks, exports, and AI-oriented artifacts can be derived reproducibly.

This RFC defines the project's stable architectural principles. Component-specific behavior is delegated to later RFCs.

## Motivation

Many AI projects begin by collecting text or assembling task-specific datasets. That approach can produce useful artifacts, but knowledge, provenance, hierarchy, and relationships often remain implicit and difficult to maintain.

IKG adopts the opposite direction: knowledge is modeled explicitly first. Derived artifacts are generated from that governed source rather than maintained as independent sources of truth.

## Core principles

### Ontology first

The ontology is designed before large-scale data generation. New content must fit a documented structure or motivate an explicit evolution of that structure.

### Knowledge Graph as source of truth

The canonical ontology and Knowledge Graph are the project's primary source of truth. JSONL, CSV, SQLite, GraphML, Neo4j, RDF, Q&A datasets, RAG indexes, and similar outputs are derived artifacts.

Derived artifacts must not silently become competing canonical sources.

### Stable identifiers

Every node has a stable identifier. Labels, descriptions, placement, and metadata may evolve, but an established identifier is treated as a public contract. Removal or replacement must be explicit and traceable.

### Human governance

AI may propose, assist, extract, compare, or review. It does not independently approve canonical knowledge. Significant changes require human review through the project contribution process.

### Reproducibility

The same repository state must produce the same canonical graph and deterministic derived outputs, except where an artifact is explicitly documented as probabilistic.

### Separation of responsibilities

Structural validation, semantic assistance, export, generation, and governance are separate concerns. A component must not silently assume authority belonging to another component.

## Logical architecture

```text
Knowledge
    ↓
Ontology
    ↓
Knowledge Graph
    ↓
Validator
    ↓
Exporters and Dataset Generators
    ↓
Applications, RAG, Benchmarks and Model Training
```

The Knowledge Graph is the center of the ecosystem. Exporters and generators consume canonical knowledge; they do not redefine it.

## Ontology hierarchy

The initial canonical hierarchy is:

```text
Macroarea
    ↓
Area
    ↓
Sottoarea
    ↓
Concetto
```

This four-level hierarchy provides the project's initial organizational backbone. Cross-domain and semantic relationships may connect concepts without replacing the canonical containment hierarchy.

Changes to the hierarchy require a dedicated RFC because they affect identifiers, validation, contribution workflows, and downstream consumers.

## Software components

### Ontology

Stores the canonical node structure and the data required to build the graph.

### Graph builder

Constructs the in-memory or persisted graph deterministically from canonical ontology data.

### Validator

Checks objective, deterministic rules concerning schema, identifiers, hierarchy, references, and supported relations. It reports violations but does not decide scientific truth.

### Exporters

Produce external representations such as JSONL, CSV, SQLite, GraphML, Neo4j-oriented data, RDF, or other documented formats.

### Dataset generators

Produce task-oriented artifacts such as question-answer pairs, flashcards, classification samples, benchmarks, or RAG-ready records from the canonical graph.

### AI reviewer

Provides non-binding semantic suggestions, including possible duplicates, missing concepts, questionable placement, or candidate relationships. It is separate from the deterministic Validator.

### Command-line interface

Offers a consistent entry point for validation, statistics, export, and future generation workflows.

## Validation and AI policy

The Validator and AI Reviewer have different authority:

- The **Validator** evaluates deterministic project rules and may block invalid changes.
- The **AI Reviewer** produces probabilistic suggestions and cannot approve, reject, or modify canonical knowledge on its own.
- The **community and maintainers** decide whether semantic proposals enter the graph.

The governing principle is:

> **AI proposes. Software verifies. The community decides.**

## Contribution lifecycle

The expected lifecycle for canonical changes is:

```text
Proposal or contribution
        ↓
Pull request
        ↓
Deterministic validation
        ↓
Human review
        ↓
Merge
        ↓
Versioned release
```

AI-assisted contributions follow the same process and must be reviewable by humans.

## Governance

IKG is designed for collaboration across technical and subject-matter domains. Domain maintainers may review specific areas of knowledge, while software maintainers govern shared tooling and compatibility.

Project decisions with long-term architectural impact should be documented through the RFC process. Accepted RFCs are frozen; substantial revisions require a new RFC that supersedes or amends the earlier decision.

## Compatibility commitments

The following are treated as compatibility-sensitive:

- stable node identifiers;
- the canonical ontology hierarchy;
- public export formats;
- validator exit behavior and rule meaning;
- documented command-line interfaces;
- release and deprecation procedures.

Changes to these areas require explicit review and, where appropriate, migration guidance.

## Non-goals

This RFC does not define:

- the final schema of a Concept node;
- the complete semantic-relation vocabulary;
- validator implementation details;
- a specific graph database;
- a specific LLM, embedding model, or AI provider;
- the final dataset-generation strategy.

Those decisions belong to dedicated RFCs.

## Future RFCs

The planned sequence is:

- RFC-0002 — IKG Validator Architecture;
- RFC-0003 — Validation Rule Registry;
- RFC-0004 — Knowledge Graph Data Model;
- RFC-0005 — Relation Model;
- RFC-0006 — Import and Export;
- RFC-0007 — Dataset Generator;
- RFC-0008 — AI Reviewer.

## Decision state

This RFC is **Draft Frozen**: its text is now stable for initial community review. It has not yet reached Accepted status. Material changes after review should be explicit, justified, and recorded before acceptance.