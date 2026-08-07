# White-paper records

## Runtime-compatible normalized JSONL

Required top-level keys are `artifact_type`, `canonical_key`, `title`, `date`, `fields`,
`signals`, `evidence`, and `warnings`. Use `artifact_type: "white-papers"`.

Exact candidate-neutral example:

```json
{"artifact_type":"white-papers","canonical_key":"white-paper|doi|10.5555/example.2024.7|revision|2","title":"Reliable Control Planes at Scale","date":"2024-07-15","fields":{"published_date":"July 2024","type":"Technical White Paper","domain":"Distributed Systems","website":"Example Research Library","publisher":"Example Research Institute","authors":["Alex Example","Jordan Sample"],"document_id":"ERI-WP-2024-07","doi":"10.5555/example.2024.7","revision":"2","canonical_url":"https://example.org/research/reliable-control-planes","content_hash":"sha256:0123456789abcdef","supersedes":"white-paper|doi|10.5555/example.2024.7|revision|1"},"signals":{"name":1.0,"affiliation":0.9,"collaborators":0.8,"topic":0.8,"geography":null,"timeline":0.9,"creator_role":1.0,"cross_source":1.0},"evidence":[{"evidence_id":"wp-001-byline","source_url":"https://example.org/research/reliable-control-planes-v2.pdf","retrieved_at":"2026-08-07T06:00:00Z","authority_rank":1,"field":"authors","raw_value":"Alex Example; Jordan Sample","normalized_value":"Alex Example;Jordan Sample","extraction_method":"pdf"},{"evidence_id":"wp-002-doi","source_url":"https://example.org/research/reliable-control-planes","retrieved_at":"2026-08-07T06:01:00Z","authority_rank":1,"field":"doi","raw_value":"https://doi.org/10.5555/EXAMPLE.2024.7","normalized_value":"10.5555/example.2024.7","extraction_method":"html"}],"warnings":[]}
```

Evidence assertions must retain raw and normalized values. An acknowledgement or PDF metadata
claim may be retained as evidence, but must use a warning and cannot set `creator_role` positive.

## Compatibility schema

```text
Title,Published Date,Type,Domain,Website
```

`Website` is a human-readable publisher/source label, not necessarily a URL.

## Enriched compatibility schema

```text
record_id,title,published_date,type,domain,website,publisher,authors,document_id,
doi,revision,canonical_url,content_hash,identity_confidence,record_confidence,
evidence_coverage,decision,confidence_reasons,source_urls,retrieved_at
```

Additional linkage fields such as `supersedes` may be retained by the runtime, but the fields
above are required. Use ISO dates when complete, semicolon-separated sorted multivalues, and stable
record IDs derived from the versioned canonical key.
