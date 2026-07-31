# Contribuire

[Italiano](./CONTRIBUTING.md) | [English](../../CONTRIBUTING.md)

Grazie per l'interesse verso Italian Knowledge Graph.

Il progetto è attualmente in fase di sviluppo attivo. I contributi devono
migliorare l'ontologia preservando coerenza, tracciabilità e identificativi
stabili.

## Tipi di contributo

I contributi possono includere:

- proporre macroaree, aree, sottoaree o concetti mancanti;
- correggere label o descrizioni;
- segnalare nodi duplicati o collocati erroneamente;
- migliorare gli strumenti di validazione;
- aggiungere exporter;
- migliorare documentazione e test.

## Regole dell'ontologia

Ogni nodo deve contenere almeno:

- `id`
- `label`
- `type`
- `parent_id`
- `description`
- `language`

Gerarchia consentita:

```text
macroarea → area → sottoarea → concetto
```

Regole:

1. Gli ID devono essere univoci, stabili, in minuscolo e usare underscore.
2. Un nodo deve fare riferimento a un parent esistente, eccetto le macroaree.
3. Label e descrizioni devono essere scritte in italiano.
4. Le descrizioni devono essere concise, neutrali e non ambigue.
5. Non rinominare un ID esistente senza documentare una migrazione.
6. I collegamenti tra domini devono essere rappresentati come relazioni
   semantiche, non duplicando i nodi.
7. I file generati non devono essere modificati manualmente quando esiste un
   file sorgente.

## Dati canonici dell'ontologia

I record dell'ontologia sono mantenuti in `ontology/macroareas.json`,
`ontology/areas.json` e `ontology/subareas.json`. Mantieni l'ordinamento dei
record, le label, le descrizioni, le relazioni parent e gli identificativi
stabili, salvo che la modifica sia proposta e revisionata esplicitamente.

Dopo aver modificato i dati canonici dell'ontologia, rigenera il seed di
compatibilità runtime:

```bash
python scripts/generate_seed.py
```

Non modificare direttamente `ontology/seed_compressed.py`. È un output generato
deterministicamente e la CI verifica che corrisponda ai JSON canonici. Il file
recuperato `ontology/legacy_ontology_source.py` rimane nel repository unicamente
come provenienza della migrazione.

La generazione non valida il significato o la qualità delle modifiche
all'ontologia. Il Validator deterministico rimane autorevole.

## Workflow proposto

1. Apri una Issue che descriva la modifica.
2. Crea un branch mirato.
3. Modifica la fonte dell'ontologia o gli strumenti.
4. Esegui Validator e test.
5. Apri una Pull Request con una spiegazione chiara.

## Messaggi di commit

Quando possibile, usa messaggi concisi in stile conventional:

```text
feat: add concept schema
fix: remove orphan subarea
validate: detect duplicate node IDs
docs: clarify ontology conventions
```

## Pull Request

Una Pull Request deve spiegare:

- cosa è cambiato;
- perché la modifica è necessaria;
- quali nodi dell'ontologia sono interessati;
- se cambiano identificativi o artefatti generati;
- come è stata validata la modifica.

## Qualità dei contenuti

L'ontologia non è destinata a codificare opinioni personali o affermazioni
promozionali. Gli argomenti controversi devono essere descritti in modo neutrale
e, quando opportuno, includere provenienza e più prospettive riconosciute.
