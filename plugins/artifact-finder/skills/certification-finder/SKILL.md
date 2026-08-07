---
name: certification-finder
description: Discover and verify public professional certification instances, renewal lineage, and issuer-backed current status without bypassing privacy controls.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(*), Task
argument-hint: "candidate_config=<path> consent_confirmed=<true|false> [output_dir=<path>]"
---

# Certification Finder

Find one record per issued credential instance. Preserve renewals as separate linked records and
report validity only when supported by issuer evidence.

## Preconditions and shared policy

The coordinator must validate `consent_confirmed=true`, load the plugin-root candidate
configuration once, and pass this workflow an immutable profile. Do not reopen, rewrite, or
embed candidate-specific details.

Read:

- `../artifact-finder/references/identity-policy.md`
- `../artifact-finder/references/evidence-policy.md`
- `../artifact-finder/references/confidence-policy.md`
- `../artifact-finder/references/output-contracts.md`

## Multi-agent workflow

Launch at least two discovery agents:

1. **Issuer agent**: searches issuer-controlled credential catalogs and public verification
   endpoints, starting from credential families and issuer names rather than broad name-only
   queries.
2. **Credential-platform agent**: searches public digital credential platforms and any
   user-provided public verification URLs.

Optional agents may inspect public professional profiles, employer biographies, or
user-provided certificate files as corroboration. If both mandatory strategies use one
provider, disclose that provider independence was not achieved.

Workers emit assertions only. Normalize and deduplicate their output, then submit the complete
evidence corpus to the run's single authoritative higher-layer identity supervisor. The
supervisor makes final attribution decisions; a focused worker cannot self-approve a record.

## Verification and privacy rules

- Prefer issuer-controlled pages, then credential platforms linking to the issuer.
- Capture credential name, issuer, level, issue date, expiration date, public credential ID,
  status, platform, and verification URL only when public.
- Never guess credential IDs, enumerate private identifiers, bypass login, solve access
  controls, use private verification codes, or expose a certificate number supplied privately.
- A user-provided private file may support a private audit assertion but its private identifier
  must be redacted from normalized and compatibility outputs.
- Absence from a public registry, a blocked page, or missing verification is `unknown`, never
  `invalid`.
- Rank-5 snippets may discover a candidate but cannot establish issuance, validity, revocation,
  expiration, or identity.

## Canonicalization, renewal, and status

Canonical grain is one issued credential instance.

Canonical key priority:

1. normalized issuer plus public stable credential ID;
2. normalized issuer, credential family/name, level, and issue date;
3. a versioned hash of the same normalized public fields when no stable ID exists.

Merge duplicate representations of the same instance. Never merge a renewal into its prior
instance. Link renewal records with `renews`/`renewed_by`, retaining issue and expiration dates
for each instance.

Allowed normalized statuses are `active`, `expired`, `revoked`, and `unknown`.

- `revoked` requires current issuer evidence.
- `expired` requires an issuer expiration date or explicit issuer status.
- `active` requires issuer evidence or a current issuer-backed validity interval.
- Conflicting or stale evidence resolves to `unknown` or a supervisor-requested targeted search,
  with the conflict preserved.

Write every observed or derived status transition to `status-events.jsonl` with effective date,
retrieval time, evidence IDs, source authority, and derivation rule.

## Normalized record example

```json
{
  "artifact_type": "certifications",
  "canonical_key": "issuer.example|cloud-architect|public-credential-123",
  "title": "Example Cloud Architect",
  "date": "2025-03-01",
  "fields": {
    "certification": "Example Cloud Architect",
    "published_date": "2025-03-01",
    "type": "Professional Certification",
    "issuer": "Example Issuer",
    "where": "Example Issuer",
    "level": "Professional",
    "issue_date": "2025-03-01",
    "expiration_date": "2028-03-01",
    "renewal_date": "",
    "status": "active",
    "public_credential_id": "public-credential-123",
    "verification_url": "https://issuer.example/credentials/public-credential-123"
  },
  "signals": {
    "name": 1.0,
    "affiliation": null,
    "collaborators": null,
    "topic": 0.9,
    "geography": null,
    "timeline": 1.0,
    "creator_role": 1.0,
    "cross_source": 0.8
  },
  "evidence": [
    {
      "evidence_id": "ev-cert-001",
      "source_url": "https://issuer.example/credentials/public-credential-123",
      "retrieved_at": "2026-01-15T12:00:00Z",
      "authority_rank": 1,
      "field": "status",
      "raw_value": "Active through March 1, 2028",
      "normalized_value": "active",
      "extraction_method": "structured"
    }
  ],
  "warnings": []
}
```

## Exact output schemas

`certifications.csv`:

```text
Certification,Published Date,Type,Where
```

`Published Date` is the issue date when known. `Where` is the issuer or public credential
platform, preferring the issuer.

`certifications.enriched.csv`:

```text
record_id,certification,type,issuer,where,level,issue_date,expiration_date,renewal_date,status,public_credential_id,verification_url,identity_confidence,record_confidence,status_confidence,evidence_coverage,decision,confidence_reasons,source_urls,retrieved_at
```

Use empty strings for unknown values. Keep raw partial dates in evidence, use ISO dates when
complete, sort multivalue fields lexicographically, and produce stable IDs from versioned
canonical keys.

## Audit and degraded modes

Produce workflow entries in `query-plan.json`, `identity-decisions.jsonl`,
`dedup-decisions.jsonl`, `status-events.jsonl`, `conflicts.jsonl`, `run-report.json`, and
`source-snapshots/`. Record issuer/platform coverage, privacy gates, redactions, blocked
verification, stale evidence, renewal links, and unknown-status reasons.

- A successful issuer search with no match is not proof of invalidity.
- Mark the workflow degraded for blocked/private verification, rate limits, stale status, one
  provider, unresolved renewal lineage, or cached-only evidence.
- Return partial results when some credential families were not searchable.
- Fail only under the shared hard-failure rules; do not fail merely because no public credential
  is found.

After supervisor decisions and reconciliation, append normalized JSONL records to the
coordinator's record file. The master skill calls `scripts/run.py`; when invoked alone, this
skill calls it with the validated candidate path, records file, output directory, and
`--consent-confirmed`.

