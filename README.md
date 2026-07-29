# Italian Knowledge Graph

<p align="center">
  <img src="assets/logo.svg" alt="Italian Knowledge Graph logo" width="620">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-early%20development-orange" alt="Status: early development">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-Apache--2.0-green" alt="Apache 2.0 license">
</p>

An open-source project for building a structured, reusable knowledge graph in Italian.

The project models knowledge through a hierarchical structure:

```text
Macroarea
  └── Area
      └── Sottoarea
          └── Concetto
```

The graph is intended to be a stable source from which multiple downstream artifacts can be generated: JSONL datasets, RAG knowledge bases, fine-tuning datasets, CSV, SQLite, GraphML, RDF/OWL and Neo4j imports.

## Current seed

The first imported seed contains:

- 48 macroareas
- 471 areas
- 710 subareas
- 1,229 total nodes
- 1,181 hierarchical `CONTAINS` edges

The canonical ontology is maintained in the human-readable
`ontology/macroareas.json`, `ontology/areas.json`, and
`ontology/subareas.json` files. `ontology/seed_compressed.py` is a deterministic
generated compatibility artifact and must not be edited directly.

Regenerate it with:

```bash
python scripts/generate_seed.py
```

The recovered original source is retained in
`ontology/legacy_ontology_source.py` for migration provenance.

## Ontology Editor

The offline Ontology Editor is the official interface for changing canonical
ontology records. Start it from the repository root:

```bash
python run_editor.py
```

Then open `http://127.0.0.1:7777`.

To use a different port:

```bash
python run_editor.py --port 8888
```

The editor works directly with the canonical JSON files, stages changes in
memory, and validates the complete ontology before saving. Invalid changes are
never written. A successful save also regenerates `ontology/seed_compressed.py`.

The selected node remains highlighted after refreshes and saves. Use **Add
child** to create the correct child type for the current selection; concept
creation is shown but remains disabled. The editor suggests deterministic IDs
from the parent and label while preserving manual overrides.

Search matches IDs, labels, and descriptions without requiring matching accents.
Matching branches expand automatically while their ancestors remain visible.
The collapsible validation panel reports the authoritative Validator messages,
and its node references can be used for navigation.

Edited forms are marked **Unsaved changes**. Discard restores committed data,
and the editor warns before navigation or page closure when changes are pending.

Use the editor instead of modifying ontology JSON manually. The UI is an editing
interface; the deterministic Validator remains the authoritative source of
truth.

### Importazione ontologie

Il pulsante **Importa Ontologia** accetta Python, JSON, YAML, Markdown e DOCX.
I file Python nel formato Kimi `add_node`/`ONTO` vengono analizzati staticamente
e non sono mai eseguiti. YAML e DOCX sono letti da parser interni basati
esclusivamente sulla libreria standard. Il formato viene riconosciuto
automaticamente da un registro di parser estendibile.

L'import manager separa parsing, conversione nel modello canonico, validazione,
anteprima e applicazione. I file selezionati sono trasferiti come byte originali,
senza Base64. L'anteprima elenca nodi, relazioni, normalizzazioni automatiche,
collisioni, duplicati, informazioni, warning ed errori bloccanti. I warning che
comportano perdita di proprietà devono essere accettati esplicitamente.

La modalità assistita richiede la conferma delle trasformazioni. La modalità
automatica applica le trasformazioni deterministiche sicure previste dagli RFC,
ma non elimina dati senza un consenso esplicito. Al termine viene mostrato un
Import Report con file, formato, parser, conversioni, warning gestiti, file
modificati e conteggi finali.

La conferma aggiorna i JSON canonici e rigenera il seed compresso. Tipi, livelli
o proprietà che non possono essere rappresentati dagli RFC correnti non
modificano il repository: vengono segnalati prima dell'importazione.

I tipi esterni vengono risolti dal Mapping Engine del Canonical Converter. Le
regole note sono conservate in `ontology/import_mappings.json` e vengono
applicate automaticamente. Un tipo sconosciuto appare nella Preview come
mapping richiesto, senza essere classificato immediatamente come errore.
L'utente può associarlo a un tipo canonico, salvare la regola e ricalcolare
l'anteprima sullo stesso file. Soltanto la struttura risultante che non può
rispettare la gerarchia canonica viene riportata come errore bloccante.

### Knowledge Quality Center

La finestra **Knowledge Quality** è indipendente dal modulo di editing e contiene
Dashboard, Errori, Warning, Copertura, Statistiche, Attività e Checklist. Ogni
finding associato a un nodo consente di aprirlo direttamente nell'editor.

Il Knowledge Quality Score aggrega in modo deterministico completezza,
integrità, coerenza, documentazione e copertura. I controlli implementano il
protocollo `QualityCheck` e sono registrati nel `QualityRegistry`: nuovi
controlli possono quindi essere aggiunti senza modificare l'aggregatore.

Lo score è uno strumento diagnostico. Il Validator deterministico rimane la
fonte autorevole per stabilire se l'ontologia può essere salvata.

## Community review

This is an early, non-authoritative ontology seed. Feedback is especially useful on:

- missing or misplaced disciplines;
- ambiguous labels and descriptions;
- duplicate or overlapping branches;
- hierarchy balance;
- stable naming and identifier conventions;
- the future `Concetto` level and semantic relations.

Use GitHub Issues for proposals and Pull Requests for reviewed changes. See `CONTRIBUTING.md`, `docs/ARCHITECTURE.md` and `docs/NODE_SCHEMA.md`.

## Quick start

Requires Python 3.10 or later.

```bash
python -m pip install -r requirements-dev.txt
python -m validators.validate_ontology
pytest
```

Export formats:

```bash
python -m exporters.export_jsonl --output-dir datasets
python -m exporters.export_csv --output-dir datasets
python -m exporters.export_sqlite --output datasets/ontology.sqlite
python -m exporters.export_graphml --output datasets/ontology.graphml
```

## Current status

- [x] Repository foundation
- [x] Complete initial ontology seed imported
- [x] Macroareas, areas and subareas defined
- [ ] Concepts
- [ ] Semantic cross-relations
- [x] Initial structural validator
- [x] JSONL, CSV, SQLite and GraphML exporters
- [x] Automated tests and GitHub Actions
- [x] Community issue and pull request templates
- [ ] Dataset generator
- [ ] Public release

## Project principles

- The ontology is the source of truth.
- Generated datasets are derived artifacts.
- Node identifiers must remain stable over time.
- Every node should be machine-readable and human-reviewable.
- Contributions should preserve structural consistency and traceability.

## Repository structure

```text
italian-knowledge-graph/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   └── pull_request_template.md
├── assets/
│   └── logo.svg
├── docs/
├── ontology/
├── exporters/
├── validators/
├── tests/
├── CHANGELOG.md
├── CITATION.cff
├── CONTRIBUTING.md
├── pyproject.toml
└── README.md
```

## Status notice

The repository is under active development. The ontology is not yet complete or authoritative and should be treated as a community-reviewed seed.

## License

Licensed under the Apache License 2.0. See `LICENSE` for details.
