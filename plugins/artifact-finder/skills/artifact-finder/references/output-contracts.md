# Output Contracts

The runtime accepts normalized JSONL records. Each line must contain:

```json
{
  "artifact_type": "patents",
  "canonical_key": "US|application|12345678",
  "title": "Artifact title",
  "date": "2022-01-15",
  "fields": {},
  "signals": {
    "name": 1.0,
    "affiliation": 1.0,
    "collaborators": 0.8,
    "topic": 0.7,
    "geography": null,
    "timeline": 1.0,
    "creator_role": 1.0,
    "cross_source": 1.0
  },
  "evidence": [],
  "warnings": []
}
```

Run:

```text
python plugins/artifact-finder/scripts/run.py \
  --candidate-config plugins/artifact-finder/candidate.config.json \
  --records <normalized-records.jsonl> \
  --output-dir <output-directory> \
  --consent-confirmed
```

Outputs include `<canonical-name-slug>.md`, compatibility CSVs, enriched CSVs,
`identity-decisions.jsonl`, and `run-manifest.json`.
