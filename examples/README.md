# Examples

Generate and inspect the ontology locally:

```bash
python -m validators.validate_ontology
python -m exporters.export_jsonl --output-dir datasets
python -m exporters.export_csv --output-dir datasets
python -m exporters.export_sqlite --output datasets/ontology.sqlite
python -m exporters.export_graphml --output datasets/ontology.graphml
python -m exporters.export_neo4j --output-dir datasets/neo4j
```

Generated artifacts are reproducible outputs and should not be edited manually.
