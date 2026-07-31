# Node and edge schema

## Node

Required fields:

```json
{
  "id": "mat_an_derivate",
  "label": "Derivate",
  "type": "sottoarea",
  "parent_id": "mat_analisi",
  "description": "Definizione, regole e applicazioni",
  "language": "it"
}
```

Allowed hierarchy types:

- `macroarea`: `parent_id` must be `null`
- `area`: parent must be a `macroarea`
- `sottoarea`: parent must be an `area`
- `concetto`: parent must be a `sottoarea` or another concept when explicitly supported

Supported optional fields are:

- `aliases`: list of non-empty strings;
- `sources`: list of structured source objects;
- `notes`: list of non-empty strings;
- `relations`: list of structured relationship references.

Missing optional fields are equivalent to empty lists. Source objects and
relationship references are defined by
[RFC-0010](rfc/RFC-0010-canonical-entity-metadata.md).

Other fields such as `tags`, `difficulty`, `importance`, and `status` remain
planned.

## Edge

```json
{
  "source": "mat_analisi",
  "target": "mat_an_derivate",
  "relation": "CONTAINS"
}
```

Current relation: `CONTAINS`.

`CONTAINS` is canonically derived from `parent_id` and must not be duplicated in
the optional `relations` property.

Planned semantic relations include `RELATED_TO`, `REQUIRES`, `IS_A`, `PART_OF`, `CONTRASTS_WITH` and `APPLIES_TO`.
