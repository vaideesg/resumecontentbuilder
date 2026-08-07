# Patent Record Schema

## Normalized JSONL

Each line must contain exactly these top-level fields:

```json
{
  "artifact_type": "patents",
  "canonical_key": "US|application|12345678",
  "title": "Artifact title",
  "date": "2022-01-15",
  "fields": {
    "family_id": "",
    "jurisdiction": "US",
    "application_number": "12345678",
    "publication_numbers": [],
    "grant_numbers": [],
    "patent_number": "",
    "type": "Application",
    "filed": "2022-01-15",
    "filing_date": "2022-01-15",
    "current_status": "Application",
    "status_effective_date": "",
    "inventors": [],
    "assignees": [],
    "continuity_type": "",
    "parent_application": "",
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
      "source_url": "https://authority.example/record",
      "retrieved_at": "2026-08-07T00:00:00Z",
      "authority_rank": 1,
      "field": "application_number",
      "raw_value": "12/345,678",
      "normalized_value": "12345678",
      "extraction_method": "structured"
    }
  ],
  "warnings": []
}
```

Rules:

- `date` equals `fields.filing_date` when known.
- `canonical_key` is `JURISDICTION|application|NORMALIZED_APPLICATION_NUMBER`.
- `publication_numbers`, `grant_numbers`, `inventors`, and `assignees` are sorted unique arrays.
- `patent_number` is the compatibility display grant number, or `""`.
- `type` and `current_status` are exactly `Grant`, `Application`, or `Abandoned`.
- `filed` is the human-readable compatibility date; `filing_date` is ISO `YYYY-MM-DD` when known.
- `continuity_type` uses the issuing authority's normalized relationship, such as
  `continuation`, `divisional`, `continuation-in-part`, `reissue`, or `national-stage`; otherwise
  `""`.
- Signal values are numbers from `0.0` through `1.0`, or `null` when unknown.
- `authority_rank` is an integer from 1 through 5.
- `extraction_method` is `structured`, `html`, `pdf`, `ocr`, or `manual-rule`.

## Compatibility CSV

The exact header and order are:

```text
Title,Patent Number,Application Number,Type,Filed,Inventors
```

Use UTF-8, RFC 4180 quoting, empty strings for unknown values, and semicolon-separated sorted
multivalue fields.

## Enriched field contract

The patent-specific enriched fields are:

```text
record_id,family_id,jurisdiction,application_number,publication_numbers,
grant_numbers,title,filing_date,current_status,status_effective_date,inventors,
assignees,continuity_type,parent_application,identity_confidence,record_confidence,
status_confidence,evidence_coverage,decision,confidence_reasons,source_urls,retrieved_at
```

The shared runtime derives `record_id`, confidence fields, `decision`, `source_urls`, and
`retrieved_at`; discovery supplies the remaining values through the normalized record and
evidence.

