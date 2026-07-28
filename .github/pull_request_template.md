## Summary

Describe the purpose of this pull request.

## Change type

- [ ] Ontology content
- [ ] Validator
- [ ] Exporter
- [ ] Documentation
- [ ] Test or maintenance

## Ontology checklist

- [ ] IDs are stable, lowercase and unique
- [ ] Every parent ID exists
- [ ] The hierarchy type is valid
- [ ] Descriptions are written in Italian
- [ ] No semantic duplicate is introduced
- [ ] Relevant sources are included when needed

## Validation

```bash
python -m validators.validate_ontology
pytest
```
