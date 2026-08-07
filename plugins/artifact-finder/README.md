# Artifact Finder Plugin

Discovers public professional artifacts for a consenting candidate and produces compatibility
CSVs plus auditable evidence and identity decisions.

## Skills

- `/artifact-finder`
- `/patent-finder`
- `/whitepaper-finder`
- `/article-finder`
- `/tech-talk-finder`
- `/certification-finder`
- `/standards-publication-finder`
- `/community-contribution-finder`

All skills share `candidate.config.json`. Candidate-specific names, employers, profiles, and
collaborators must not be embedded in skill instructions.

## Runtime

Discovery agents produce normalized JSONL records. Render them with:

```powershell
python plugins\artifact-finder\scripts\run.py `
  --candidate-config plugins\artifact-finder\candidate.config.json `
  --records path\to\normalized-records.jsonl `
  --output-dir artifact-results `
  --consent-confirmed
```

The standard-library runtime requires Python 3.10 or later.

## Outputs

- Artifact-specific compatibility CSVs
- Artifact-specific enriched CSVs
- `identity-decisions.jsonl`
- `run-manifest.json`

Only confirmed and probable identity matches enter compatibility CSVs by default.
