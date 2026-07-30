# Italian Knowledge Graph

[Italiano](./README.md) | [English](../../README.md)

<p align="center">
  <img src="../../assets/logo.svg" alt="Logo di Italian Knowledge Graph" width="620">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-early%20development-orange" alt="Stato: sviluppo iniziale">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-Apache--2.0-green" alt="Licenza Apache 2.0">
</p>

Italian Knowledge Graph è una piattaforma open source per costruire, validare,
migliorare, condividere e governare conoscenza strutturata in italiano.

IKG è più di un editor di ontologie. Collega fonti di conoscenza leggibili dalle
persone, regole deterministiche, analisi della qualità, export riproducibili e
contributi della community revisionabili in un unico ambiente per sviluppatori
ed esperti di dominio.

## Documentazione

La documentazione è disponibile in:

- [English](../../README.md)
- [Italiano](./README.md)

## Perché IKG

La conoscenza utile dovrebbe essere:

- **strutturata**, con identificativi, tipi e relazioni espliciti;
- **verificabile**, tramite regole deterministiche;
- **riutilizzabile**, senza essere legata a una singola applicazione;
- **collaborativa**, con modifiche revisionabili;
- **revisionabile dalle persone**, anche quando gli strumenti propongono trasformazioni;
- **indipendente dal modello**, affinché nessun provider di AI diventi fonte di verità.

Il progetto segue un principio semplice:

> **L'AI può proporre. Il Validator deterministico verifica. Le persone decidono.**

L'attuale AI Reviewer usa soltanto euristiche deterministiche. I suoi
suggerimenti sono consultivi e non sostituiscono mai i finding del Validator.

## Perché IKG è diverso?

IKG riunisce in un solo ambiente l'intero ciclo di manutenzione della
conoscenza: validazione deterministica, modifica dell'ontologia, importazione
sicura, analisi della qualità, contribuzione guidata della community ed export
deterministici.

Ogni fase rimane ispezionabile. Le fonti restano leggibili, le trasformazioni
appaiono in una Preview, la validazione è riproducibile e le decisioni
semantiche restano affidate alle persone.

## Cosa offre IKG

- **Modello canonico dell'ontologia**: fonti JSON ordinate, con identificativi
  stabili e struttura parent-child esplicita.
- **Validator deterministico**: finding riproducibili per schema, gerarchia,
  relazioni e integrità.
- **Ontology Editor offline**: applicazione FastAPI locale per navigazione,
  modifica, validazione e salvataggio sicuri.
- **Pipeline di importazione dell'ontologia**: registry dei parser, conversione
  canonica, mapping, Preview, validazione e applicazione confermata.
- **Knowledge Quality Center**: punteggio diagnostico, controlli di qualità,
  statistiche e navigazione diretta ai nodi interessati.
- **Preparazione dei contributi**: diff di sessione, report di validazione e
  qualità, pacchetti ZIP revisionabili e preparazione Git locale facoltativa.
- **Pacchetti di contributo guidato**: template DOCX deterministici per chi non
  lavora direttamente con Git o JSON.
- **Exporter deterministici**: dataset validati per machine learning in JSONL e CSV.
- **Governance guidata dagli RFC**: le decisioni architetturali sono registrate
  in [`docs/rfc/`](../rfc/README.md).

## Avviare la UI

È richiesto **Python 3.10 o successivo**. I launcher non installano Python, non
richiedono privilegi amministrativi e non scaricano codice remoto. L'editor
esegue il bind soltanto su `127.0.0.1`; i dati dell'ontologia restano locali e
non vengono inviati online.

### Windows

Fai doppio clic su `start-ikg.bat` oppure esegui direttamente il launcher PowerShell:

```powershell
.\start-ikg.ps1
.\start-ikg.ps1 --port 8888
```

### macOS

Autorizza una volta gli script locali, quindi avviali dal Terminale o fai doppio
clic su `start-ikg.command` nel Finder:

```bash
chmod +x start-ikg.sh start-ikg.command
./start-ikg.command
```

macOS Gatekeeper può mostrare un avviso per uno script scaricato da Internet.
Esamina il file e usa il normale flusso di autorizzazione di macOS; il launcher
non disabilita né aggira Gatekeeper.

### Linux

```bash
chmod +x start-ikg.sh
./start-ikg.sh
```

Tutti i launcher supportano `--port PORT`, `--no-browser` e `--check-only`. Per
impostazione predefinita il browser si apre una volta su
`http://127.0.0.1:7777`.

## Avvio rapido per sviluppatori

Richiede **Python 3.10 o successivo**. Installa e avvia l'editor:

```bash
python -m pip install -e .
python run_editor.py
```

Apri la UI locale:

```text
http://127.0.0.1:7777
```

Windows PowerShell:

```powershell
Start-Process http://127.0.0.1:7777
```

Porta personalizzata:

```bash
python run_editor.py --port 8888
```

Valida:

```bash
ikg validate graph.json
```

Esegui i test:

```bash
python -m pytest
```

Rigenera o controlla il seed runtime:

```bash
python scripts/generate_seed.py
python scripts/generate_seed.py --check
```

## Modello della conoscenza

La gerarchia canonica è:

```text
Macroarea
└── Area
    └── Sottoarea
        └── Concetto
```

`Concetto` fa già parte del modello logico del grafo, delle regole di
validazione, degli exporter di dataset e degli strumenti di review. L'attuale
popolazione dell'ontologia canonica contiene macroaree, aree e sottoaree, ma
non ancora record di concetti.

Le fonti di verità sono:

- [`ontology/macroareas.json`](../../ontology/macroareas.json)
- [`ontology/areas.json`](../../ontology/areas.json)
- [`ontology/subareas.json`](../../ontology/subareas.json)

[`ontology/seed_compressed.py`](../../ontology/seed_compressed.py) è un artefatto
generato per la compatibilità runtime. Anche dataset e pacchetti di contributo
sono artefatti derivati. I file generati non devono sostituire o modificare
silenziosamente le fonti canoniche.

## Come funziona

```text
Knowledge source
       ↓
Import pipeline / Ontology Editor
       ↓
Canonical Converter
       ↓
Deterministic Validator
       ↓
Canonical ontology
       ↓
Knowledge Quality Center
       ↓
Exporters / Contribution workflows
```

Il Canonical Converter appartiene al percorso di importazione. Le modifiche
dirette dell'editor vengono preparate in memoria e validate sull'intera
ontologia prima della scrittura dei file.

Il ciclo completo della community è:

```text
Knowledge
    ↓
Import / Editor
    ↓
Validator
    ↓
Knowledge Quality
    ↓
📦 Contribution Package
    ↓
Community
    ↓
Importa Ontologia
    ↓
Repository
```

## Ontology Editor

L'Ontology Editor è l'interfaccia supportata per le modifiche ordinarie
dell'ontologia. Funziona localmente e non richiede database né connessione di rete.

Offre:

- gerarchia espandibile con scroll indipendente della navigazione;
- ricerca per ID, Label e Description;
- ordinamento alfabetico italiano per Label visibile, senza distinzione tra maiuscole e minuscole;
- creazione, modifica, cambio di parent ed eliminazione in memoria;
- suggerimenti deterministici per gli ID;
- validazione dell'intero grafo prima della scrittura;
- protezione da parent mancanti, gerarchia non valida e ID duplicati;
- scritture atomiche dei JSON canonici;
- rigenerazione deterministica del seed dopo un salvataggio valido.

Il Validator rimane autorevole. La UI non ne duplica le regole e non scrive mai
i file dell'ontologia quando la validazione fallisce.

## Importa Ontologia

**Importa Ontologia** accetta:

- **Python** tramite parsing AST sicuro; il Python importato non viene mai eseguito;
- **JSON**;
- **YAML** tramite un parser interno basato sulla libreria standard;
- tabelle **Markdown** o contenuto JSON/YAML in blocchi delimitati;
- **DOCX** tramite parsing interno di ZIP, OOXML e XML.

I file sono elaborati come byte grezzi senza conversione Base64. La pipeline
rileva il formato, analizza i dati sorgente, applica mapping persistenti dei
tipi, converte nel modello canonico, valida il risultato completo e mostra una
Preview.

Gli errori bloccanti impediscono l'importazione. I warning che possono scartare
proprietà non canoniche richiedono accettazione esplicita. Collisioni e duplicati
sono segnalati e i dati non vengono mai eliminati silenziosamente.

## Knowledge Quality Center

Il **Knowledge Quality Center** si apre in una finestra separata e
ridimensionabile. Le sue tab comprendono:

- Dashboard
- Errori
- Warning
- Copertura
- Statistiche
- Attività
- Checklist

Le righe associate ai nodi dell'ontologia permettono di tornare direttamente
all'editor. Il Knowledge Quality Score riassume i controlli di completezza,
integrità, coerenza, documentazione e copertura.

Il punteggio è diagnostico. Non sostituisce la validazione deterministica e non
può autorizzare un salvataggio.

## Contribuire senza programmare

Gli esperti di dominio possono preparare un contributo senza modificare JSON o usare Git:

1. Apri **📦 Crea pacchetto di contributo**.
2. Seleziona un dominio, un ramo o un nodo specifico.
3. Scegli cosa completare, aggiungere o revisionare.
4. Controlla numero di nodi, campi richiesti e tempo stimato.
5. Genera il pacchetto di contributo.
6. Modifica `contribution.docx` in Microsoft Word o software compatibile.
7. Reimporta il documento con **Importa Ontologia**.
8. Controlla i warning ed esegui la validazione prima dell'integrazione.

Il pacchetto contiene:

- `contribution.docx`
- `README.txt`
- `metadata.json`

ID, tipi, label, valori della lingua e gerarchia esistenti sono protetti durante
la reimportazione. Il documento include una tabella separata per proporre nuovi
nodi. Le modifiche importate passano comunque dalla Preview, dalla conversione
e dal Validator autorevole.

## Preparare un contributo al repository

**Prepara contributo** diventa disponibile quando la sessione dell'editor
differisce dal suo stato canonico iniziale. Offre:

- riepiloghi dei nodi aggiunti, modificati, rimossi ed esclusi;
- modifiche alle relazioni parent;
- controlli deterministici di validazione e integrità;
- Quality Report e punteggi di qualità prima/dopo;
- file canonici interessati e diff leggibile;
- accettazione esplicita dei warning;
- ZIP di revisione riproducibile;
- preparazione facoltativa dei file autorizzati in un repository Git locale pulito;
- titolo di commit e descrizione della Pull Request suggeriti.

Il workflow **non** esegue `git commit`, `git push`, merge, reset, cambi di branch
o creazione di Pull Request. Le operazioni sul repository rimangono decisioni
esplicite dei maintainer.

## Ontologia attuale

I conteggi derivano dagli attuali JSON canonici e dal grafo runtime:

| Livello | Conteggio |
|---|---:|
| Macroaree | 48 |
| Aree | 471 |
| Sottoaree | 710 |
| Concetti | 0 |
| **Nodi totali** | **1.229** |
| Archi gerarchici `CONTAINS` | 1.181 |

Il modello logico supporta i concetti; l'attuale dataset canonico contiene zero
istanze di concetti.

L'ontologia è un seed della community in evoluzione, non una rappresentazione
completa o autorevole di tutta la conoscenza.

## Formati di export

Il generatore di dataset accetta un documento JSON KnowledgeGraph validato e
produce un ordinamento stabile di entità e relazioni.

JSONL:

```bash
ikg export dataset \
  --input graph.json \
  --format jsonl \
  --output dataset.jsonl
```

CSV:

```bash
ikg export dataset \
  --input graph.json \
  --format csv \
  --output dataset.csv
```

Entrambi i comandi validano prima l'input e si fermano in presenza di errori di
validazione. Gli exporter SQLite, GraphML, RDF/OWL e Neo4j non sono attualmente
implementati.

L'advisory reviewer è disponibile separatamente:

```bash
ikg review graph.json
```

## Documenti del progetto

- [`README.md`](README.md): panoramica del progetto, funzionalità attuali e avvio rapido.
- [`GETTING_STARTED.md`](GETTING_STARTED.md): guida pratica al primo utilizzo e contributo.
- [`MANIFESTO.md`](MANIFESTO.md): visione, principi e obiettivi a lungo termine.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): workflow di contribuzione e linee guida di sviluppo.
- [`LICENSE`](../../LICENSE): licenza Apache 2.0 che disciplina il progetto.

## Community

IKG supporta due percorsi di contribuzione:

```text
Developer
    ↓
GitHub
    ↓
Repository

Domain expert
    ↓
📦 Crea pacchetto di contributo
    ↓
DOCX
    ↓
Importa Ontologia
    ↓
Validator
    ↓
Repository
```

### Esperti di dominio e non sviluppatori

Usa **📦 Crea pacchetto di contributo** per selezionare un ramo gestibile
dell'ontologia, compilare un DOCX guidato e restituirlo attraverso la stessa
Preview di importazione usata dai maintainer. Non servono Git né modifiche
dirette ai JSON.

### Sviluppatori e maintainer

Usa Issue e Pull Request per modifiche a codice, ontologia, validazione e
documentazione. Esegui Validator e test prima di proporre l'integrazione.

Riferimenti del progetto:

- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md)
- [`docs/NODE_SCHEMA.md`](../NODE_SCHEMA.md)
- [`docs/AI_REVIEWER.md`](../AI_REVIEWER.md)
- [`docs/rfc/`](../rfc/README.md)
- [Indice delle regole del Validator](../validator/rules/index.md)

## Principi del progetto

- I JSON canonici dell'ontologia sono la fonte di verità.
- Gli artefatti generati devono essere riproducibili.
- Gli identificativi pubblicati rimangono stabili.
- I contenuti importati sono sempre trattati come dati.
- Il Python importato viene analizzato e mai eseguito.
- Trasformazioni e proprietà scartate sono visibili prima dell'importazione.
- La perdita silenziosa di dati non è consentita.
- Il Validator deterministico è autorevole.
- Punteggi di qualità e suggerimenti del reviewer sono consultivi.
- Le persone approvano le modifiche semantiche.
- Le dipendenze runtime sono intenzionalmente limitate a FastAPI e Uvicorn;
  parser di file, generazione DOCX e seed e creazione dei pacchetti di
  contributo usano la libreria standard di Python.

## Roadmap

### Completato

- Modelli immutabili di entità, relazioni, finding e report
- Motore di validazione deterministico e registry delle regole
- Validazione delle relazioni e caricamento retrocompatibile del grafo
- JSON canonici dell'ontologia e seed compresso deterministico
- Exporter di dataset JSONL e CSV
- Architettura AI Reviewer con euristiche deterministiche
- Ontology Editor offline
- Importer multiformato e mapping persistente dei tipi
- Knowledge Quality Center
- Workflow revisionabile dei contributi al repository
- Pacchetti di contributo guidato DOCX

### In corso

- Revisione e correzione da parte della community del seed dell'ontologia
- Allineamento della documentazione architetturale e degli RFC
- Rafforzamento dei workflow di editor e importazione con più input reali

### Pianificato

- Popolare il livello logico `Concetto` esistente nei dati canonici
- Completare la persistenza di concetti in editor e importer
- Campi o modelli canonici per fonti, sinonimi e note
- Relazioni semantiche non gerarchiche nell'ontologia mantenuta
- Ulteriori exporter deterministici
- Provider facoltativi per il reviewer, nel rispetto del ruolo solo consultivo

## Struttura del repository

```text
italian-knowledge-graph/
├── assets/                 Project visual assets
├── docs/                   Architecture, schema, validator, and RFC documents
├── ontology/               Canonical JSON and generated runtime seed
├── scripts/                Deterministic seed generator
├── src/
│   ├── editor/
│   │   ├── contribution/   Reviewable and guided contribution workflows
│   │   ├── importer/       Parsers, converter, mapping, preview, and import engine
│   │   ├── quality/        Quality checks, registry, and report service
│   │   └── static/         Offline HTML, CSS, and JavaScript UI
│   └── ikg/
│       ├── dataset/        JSONL and CSV dataset generation
│       ├── reviewer/       Advisory reviewer providers and heuristics
│       └── validator/      Deterministic validation engine and rules
└── tests/                  Unit, integration, CLI, editor, and ontology tests
```

## Stato e limitazioni

IKG è in una fase iniziale di sviluppo attivo.

- L'ontologia è ampia ma incompleta e non è un riferimento autorevole.
- `Concetto` è supportato dal modello logico e dagli strumenti, ma l'attuale
  ontologia canonica non contiene record di concetti e l'editor non offre ancora
  il workflow completo per la loro persistenza.
- Fonti, sinonimi e note mostrati nei documenti di contributo guidato non sono
  ancora campi canonici persistenti; l'importer li segnala prima dell'integrazione.
- L'ontologia mantenuta contiene attualmente soltanto relazioni gerarchiche `CONTAINS`.
- Il Knowledge Quality Score è diagnostico.
- L'AI Reviewer usa attualmente euristiche deterministiche ed è consultivo.
- L'editor è uno strumento di sviluppo locale, non un servizio multiutente ospitato.

## Licenza

Italian Knowledge Graph è distribuito con
[Apache License 2.0](../../LICENSE).
