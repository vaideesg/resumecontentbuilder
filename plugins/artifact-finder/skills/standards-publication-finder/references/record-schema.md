# Standards Publication Record Schema

## Normalized JSONL

Each line must contain exactly these top-level fields:

```json
{
  "artifact_type": "standards-publications",
  "canonical_key": "IETF|lineage|draft-example",
  "title": "Artifact title",
  "date": "2022-01-15",
  "fields": {
    "lineage_id": "draft-example",
    "published_date": "2022-01-15",
    "type": "RFC",
    "standards_body": "IETF",
    "working_group": "",
    "committee": "",
    "role": "Author",
    "identifier": "",
    "status": "RFC",
    "version": "",
    "authors_editors": [],
    "canonical_url": "https://authority.example/document",
    "url": "https://authority.example/document",
    "predecessor_ids": [],
    "successor_ids": [],
    "updates_ids": [],
    "updated_by_ids": [],
    "obsoletes_ids": [],
    "obsoleted_by_ids": [],
    "status_history": [],
    "status_confidence": 1.0
  },
  "signals": {
    "name": 1.0,
    "affiliation": null,
    "collaborators": null,
    "topic": null,
    "geography": null,
    "timeline": null,
    "creator_role": 1.0,
    "cross_source": null
  },
  "evidence": [
    {
      "evidence_id": "ev-001",
      "source_url": "https://authority.example/document",
      "retrieved_at": "2026-08-07T00:00:00Z",
      "authority_rank": 1,
      "field": "identifier",
      "raw_value": "RFC 0000",
      "normalized_value": "RFC0000",
      "extraction_method": "structured"
    }
  ],
  "warnings": []
}
```

Rules:

- `date` equals `fields.published_date` when known.
- Document keys are `BODY|lineage|NORMALIZED_LINEAGE_ID`.
- Formal non-author role keys are `BODY|role|NORMALIZED_SCOPE_ID|NORMALIZED_ROLE`.
- `canonical_url` and compatibility `url` normally contain the same authority-controlled URL.
- Relationship arrays and `authors_editors` are sorted and unique.
- `status_history` is a sorted list of compact authority-backed event strings or serialized event
  objects; each event's facts also require evidence.
- `type` uses only the publication-type vocabulary in `SKILL.md`.
- Signal values are numbers from `0.0` through `1.0`, or `null` when unknown.
- `authority_rank` is an integer from 1 through 5.
- `extraction_method` is `structured`, `html`, `pdf`, `ocr`, or `manual-rule`.

## Compatibility CSV

The exact header and order are:

```text
Title,Published Date,Type,Standards Body,Working Group,Role,Identifier,Status,URL
```

Use UTF-8, RFC 4180 quoting, empty strings for unknown values, and semicolon-separated sorted
multivalue fields.

## Enriched field contract

The standards-specific enriched fields are:

```text
record_id,lineage_id,title,published_date,type,standards_body,working_group,
committee,role,identifier,status,version,authors_editors,canonical_url,
predecessor_ids,successor_ids,updates_ids,updated_by_ids,obsoletes_ids,
obsoleted_by_ids,status_history,identity_confidence,record_confidence,
status_confidence,evidence_coverage,decision,confidence_reasons,source_urls,
retrieved_at
```

The shared runtime derives `record_id`, confidence fields, `decision`, `source_urls`, and
`retrieved_at`; discovery supplies the remaining values through the normalized record and
evidence.
