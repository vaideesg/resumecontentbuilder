# Technical-talk records

## Runtime-compatible normalized JSONL

Use `artifact_type: "tech-talks"` and the runtime top-level keys `artifact_type`,
`canonical_key`, `title`, `date`, `fields`, `signals`, `evidence`, and `warnings`.

Exact candidate-neutral example:

```json
{"artifact_type":"tech-talks","canonical_key":"talk|event-id|exconf-session-204|delivery|2025-05-14","title":"Operating Resilient Distributed Systems","date":"2025-05-14","fields":{"talk_series_id":"talk-series|operating-resilient-distributed-systems","type":"Conference Talk","delivery_date":"2025-05-14","publication_date":"2025-05-20","published_date":"May 14, 2025","event":"Example Systems Conference 2025","organizer":"Example Systems Foundation","where":"Example Systems Conference 2025","venue_mode":"in-person","speaker_role":"speaker","co_speakers":["Jordan Sample"],"recording_url":"https://video.example.org/watch/exconf-204","slides_url":"https://slides.example.org/exconf-204","duration_minutes":"42"},"signals":{"name":1.0,"affiliation":0.9,"collaborators":0.8,"topic":0.9,"geography":0.8,"timeline":1.0,"creator_role":1.0,"cross_source":1.0},"evidence":[{"evidence_id":"talk-001-schedule","source_url":"https://events.example.org/2025/sessions/204","retrieved_at":"2026-08-07T06:30:00Z","authority_rank":1,"field":"delivery_date","raw_value":"May 14, 2025, 10:00 AM","normalized_value":"2025-05-14","extraction_method":"html"},{"evidence_id":"talk-002-upload","source_url":"https://video.example.org/watch/exconf-204","retrieved_at":"2026-08-07T06:31:00Z","authority_rank":2,"field":"publication_date","raw_value":"Published May 20, 2025","normalized_value":"2025-05-20","extraction_method":"html"}],"warnings":[]}
```

For another verified delivery of the same talk, retain the same `talk_series_id` but use a new
delivery-specific canonical key. If delivery date is unknown, `date` and `published_date` may use
the earliest authoritative upload date only with a warning and empty `delivery_date`.

## Compatibility schema

```text
Talk,Published Date,Type,Where
```

## Enriched compatibility schema

```text
record_id,talk_series_id,title,type,delivery_date,publication_date,event,
organizer,where,venue_mode,speaker_role,co_speakers,recording_url,slides_url,
duration_minutes,identity_confidence,record_confidence,evidence_coverage,
decision,confidence_reasons,source_urls,retrieved_at
```

Use ISO dates when complete, sorted semicolon-separated multivalues, and stable record IDs derived
from delivery-specific canonical keys.
