# Per iniziare

[Italiano](./GETTING_STARTED.md) | [English](../../GETTING_STARTED.md)

> **Sei qui per la prima volta?**
>
> Se questa è la tua prima visita, segui questa guida dall'inizio alla fine.
> In circa 10 minuti creerai e validerai il tuo primo contributo a Italian
> Knowledge Graph.

Italian Knowledge Graph funziona localmente sul tuo computer. Questa guida ti
accompagna dal download del progetto alla preparazione e all'importazione del
tuo primo contributo guidato.

## 1. Prerequisiti

Sono necessari:

- Python 3.10 o successivo;
- Windows, macOS o Linux;
- un browser web;
- Microsoft Word o un altro editor compatibile con DOCX.

Git è facoltativo. Serve solo se scegli di clonare il repository invece di
scaricare un archivio ZIP.

L'editor e l'ontologia funzionano localmente. Nessun dato dell'ontologia viene
inviato a servizi cloud.

## 2. Ottenere il progetto

### Clonare con Git

```bash
git clone https://github.com/stonamatteo-a11y/italian-knowledge-graph.git
cd italian-knowledge-graph
```

### Scaricare uno ZIP

1. Apri il repository Italian Knowledge Graph su GitHub.
2. Seleziona **Code**, quindi **Download ZIP**.
3. Estrai l'archivio.
4. Apri un terminale nella directory `italian-knowledge-graph` estratta.

## 3. Avviare la UI

Il launcher controlla Python e il progetto locale prima dell'avvio. Se mancano
pacchetti Python richiesti, segui il messaggio di errore oppure installa
manualmente il progetto con:

```bash
python -m pip install -e .
```

### Windows

Fai doppio clic su:

```text
start-ikg.bat
```

In alternativa, usa PowerShell:

```powershell
.\start-ikg.ps1
```

### macOS

Autorizza i launcher una sola volta:

```bash
chmod +x start-ikg.sh start-ikg.command
```

Quindi fai doppio clic su `start-ikg.command` nel Finder oppure esegui:

```bash
./start-ikg.command
```

L'alternativa da Terminale è:

```bash
./start-ikg.sh
```

### Linux

```bash
chmod +x start-ikg.sh
./start-ikg.sh
```

Il launcher avvia l'editor locale e apre automaticamente il browser predefinito
all'indirizzo `http://127.0.0.1:7777`.

## 4. Esplorare il Knowledge Graph

Il pannello sinistro contiene la gerarchia dell'ontologia.

- Espandi un ramo per esplorarne i figli.
- Usa Search per cercare un ID, una Label o una Description.
- Seleziona un nodo per visualizzarne i dettagli nell'editor.

## 5. Creare il primo contributo

Scegli un dominio o un ramo nella gerarchia, quindi segui questo flusso:

```text
Select a domain
        ↓
📦 Crea pacchetto di contributo
        ↓
Choose the number of nodes
        ↓
Generate the package
```

Scegli i campi da revisionare, seleziona un limite di nodi, controlla il
riepilogo e seleziona **📦 Crea pacchetto di contributo**.

Lo ZIP generato contiene `contribution.docx`, `README.txt` e `metadata.json`.

## 6. Compilare il DOCX

1. Apri `contribution.docx`.
2. Compila i campi contrassegnati con **Da compilare**.
3. Non modificare i campi contrassegnati con **Protetto**.
4. Usa la sezione finale per le proposte se vuoi suggerire una nuova voce.
5. Salva il documento in formato DOCX.

Puoi lasciare vuoti i campi ai quali non vuoi contribuire.

## 7. Importare il contributo

Torna all'editor e segui questo flusso:

```text
Importa Ontologia
        ↓
Select contribution.docx
        ↓
Preview
        ↓
Validator
        ↓
Import
```

La Preview mostra i nodi rilevati, le modifiche proposte, i warning e gli
errori bloccanti. Controlla queste informazioni prima di confermare.

Nessuna modifica all'ontologia viene applicata senza passare dalla validazione.

## 8. Validator

Il Validator deterministico controlla:

- struttura dei record e proprietà obbligatorie;
- gerarchia e riferimenti ai parent;
- identificativi e duplicati;
- relazioni supportate;
- regole di coerenza e vincoli sui contenuti obbligatori.

Il Validator produce lo stesso risultato per lo stesso input ed è il meccanismo
autorevole di accettazione delle modifiche strutturali.

Il Knowledge Quality Center fornisce un'ulteriore analisi diagnostica della
qualità. Il suo punteggio non sostituisce il Validator.

## 9. Dove trovare aiuto

- [`README.md`](README.md) offre una panoramica del progetto e i comandi di
  riferimento.
- [`MANIFESTO.md`](MANIFESTO.md) illustra la visione e i principi del progetto.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) descrive le linee guida per contribuire e
  sviluppare.
- Usa le [GitHub Issues](https://github.com/stonamatteo-a11y/italian-knowledge-graph/issues)
  per segnalare bug.
- Le GitHub Discussions possono essere usate per le domande della community,
  quando saranno abilitate.

## 10. Primo contributo completato

**Congratulazioni!**

Hai completato il tuo primo contributo a Italian Knowledge Graph.

Grazie per contribuire a migliorare la conoscenza strutturata.
