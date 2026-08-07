# Article records

## Runtime-compatible normalized JSONL

Use `artifact_type: "articles"` and the runtime top-level keys `artifact_type`, `canonical_key`,
`title`, `date`, `fields`, `signals`, `evidence`, and `warnings`.

Exact candidate-neutral example:

```json
{"artifact_type":"articles","canonical_key":"article|doi|10.5555/example.article.42","title":"Designing Observable Distributed Services","date":"2025-02-10","fields":{"published_date":"February 10, 2025","type":"Technical Article","category":"Architecture","website":"Example Engineering Journal","publisher":"Example Media","author_role":"author","co_authors":["Jordan Sample"],"doi":"10.5555/example.article.42","canonical_url":"https://example.org/articles/observable-services","archive_url":"https://archive.example.org/articles/observable-services","syndicated_urls":["https://syndication.example.net/observable-services"],"impressions":"1842","views":"","reactions":"57","comments":"8","reposts":"4","metrics_retrieved_at":"2026-08-07T06:15:00Z"},"signals":{"name":1.0,"affiliation":0.9,"collaborators":0.8,"topic":0.9,"geography":null,"timeline":1.0,"creator_role":1.0,"cross_source":1.0},"evidence":[{"evidence_id":"article-001-byline","source_url":"https://example.org/articles/observable-services","retrieved_at":"2026-08-07T06:14:00Z","authority_rank":1,"field":"author_role","raw_value":"By Alex Example and Jordan Sample","normalized_value":"author","extraction_method":"html"},{"evidence_id":"article-002-impressions","source_url":"https://example.org/articles/observable-services","retrieved_at":"2026-08-07T06:15:00Z","authority_rank":1,"field":"impressions","raw_value":"1,842 impressions","normalized_value":"1842","extraction_method":"html"}],"warnings":[]}
```

Do not emit `0` for an unavailable metric. Any non-empty metric requires field evidence and
`metrics_retrieved_at`. Non-author roles and non-professional classifications remain review
candidates, not compatibility rows.

## Compatibility schema

```text
Title,Published Date,Type,Category,Website,Impressions
```

## Enriched compatibility schema

```text
record_id,title,published_date,type,category,website,publisher,author_role,
co_authors,doi,canonical_url,archive_url,impressions,views,reactions,comments,
reposts,metrics_retrieved_at,identity_confidence,record_confidence,
evidence_coverage,decision,confidence_reasons,source_urls,retrieved_at
```

Additional syndication/revision links may be retained. Use ISO dates when complete, sorted
semicolon-separated multivalues, and stable IDs from canonical keys.
