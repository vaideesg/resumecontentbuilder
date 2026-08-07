# Artifact Finder Plugin

Discovers public professional artifacts for a consenting candidate and produces one consolidated
candidate Markdown portfolio, compatibility CSVs, and auditable identity decisions.

## Skills

- `/collect-artifacts` - autonomous end-to-end collection and candidate portfolio
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

## Demo Layout

The repository includes a complete demonstration:

```text
demo/
|-- vaideeswaran-ganesan-config.json
|-- vaideeswaran-ganesan.md
`-- output/
    |-- normalized-records.jsonl
    |-- patents.csv
    |-- patents.enriched.csv
    |-- ...other artifact CSVs...
    |-- identity-decisions.jsonl
    |-- dedup-decisions.jsonl
    |-- status-events.jsonl
    |-- conflicts.jsonl
    |-- query-plan.json
    |-- run-manifest.json
    `-- run-report.json
```

`normalized-records.jsonl` contains synthetic `[DEMO]` records. It demonstrates the output
shape and is not a factual attribution to the configured candidate.

## Configure a Candidate

Use `demo/vaideeswaran-ganesan-config.json` as an example and replace only the public candidate
evidence.

Configuration shape:

```json
{
  "schema_version": "1.0",
  "candidate": {
    "canonical_name": "Example Candidate",
    "known_name_variants": ["E. Candidate"],
    "employment": [
      {
        "company": "Example Systems",
        "aliases": ["Example Systems Inc."],
        "start_date": "2018-01-01",
        "end_date": null
      }
    ],
    "professional_profiles": [
      {
        "type": "github",
        "url": "https://github.com/example-candidate",
        "username": "example-candidate"
      }
    ],
    "known_collaborators": ["Example Collaborator"]
  }
}
```

Do not add credentials, cookies, private contact information, or non-public personal data.

## Run All Artifact Workflows

Invoke the user-facing master with only the candidate config:

```text
/collect-artifacts demo/vaideeswaran-ganesan-config.json
```

The skill autonomously launches the patent, standards, white-paper, article, technical-talk,
certification, and community workflows. Each workflow uses multiple discovery agents. One
higher-layer supervisor makes final identity and inclusion decisions across the combined corpus.

The deterministic renderer can also be demonstrated without live discovery:

```powershell
python plugins\artifact-finder\scripts\run.py `
  --candidate-config demo\vaideeswaran-ganesan-config.json `
  --records demo\output\normalized-records.jsonl `
  --output-dir demo\output `
  --portfolio-dir demo `
  --consent-confirmed
```

## Sample Output

The consolidated portfolio is generated beside the candidate config using the canonical-name
slug:

```text
demo/vaideeswaran-ganesan.md
```

Excerpt:

```markdown
# Vaideeswaran Ganesan

> **Demonstration only:** Artifact entries marked `[DEMO]` are synthetic examples
> showing output structure. They are not factual claims about the candidate.

## Artifact Counts

- **Patents:** 1
- **Standards Publications:** 1
- **White Papers:** 1
- **Articles:** 1
- **Technical Talks:** 1
- **Certifications:** 1
- **Open Source and Community Contributions:** 1

## Patents

- **[DEMO] Adaptive service recovery using dependency-aware signals** — 2022-01-15;
  Type: Grant; Patent Number: 12345678
```

## Outputs

- `<canonical-name-slug>.md` consolidated portfolio
- Artifact-specific compatibility CSVs
- Artifact-specific enriched CSVs
- `identity-decisions.jsonl`
- `run-manifest.json`

Only confirmed and probable identity matches enter compatibility CSVs by default.
