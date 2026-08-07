---
name: community-contribution-finder
description: Discover and verify meaningful open-source, package, repository, review, documentation, leadership, and summarized public community contributions.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(*), Task
argument-hint: "candidate_config=<path> consent_confirmed=<true|false> [output_dir=<path>]"
---

# Community Contribution Finder

Discover meaningful public engineering and community contributions without equating profile
presence, organization membership, repository ownership, or display-name similarity with
authorship.

## Preconditions and shared policy

The coordinator validates consent, loads `candidate_config` once, and passes an immutable
candidate profile. Candidate-specific names, accounts, employers, profiles, and collaborators
must never be embedded here.

Read:

- `../artifact-finder/references/identity-policy.md`
- `../artifact-finder/references/evidence-policy.md`
- `../artifact-finder/references/confidence-policy.md`
- `../artifact-finder/references/output-contracts.md`

## Required discovery agents

Run at least two agents, partitioned by source or strategy:

1. **Forge/history agent**: public forge profiles, repository history, pull requests, commits,
   reviews, issues, releases, contributor files, governance, and repository rename/transfer/fork
   history.
2. **Registry/community agent**: package registries, maintainer pages, public Q&A profiles,
   forums, discussions, foundations, and community role pages.

Use additional agents for independent forge providers or community platforms when available.
Record when only one provider was available. Workers emit evidence assertions, not final
identity, role, inclusion, merge, or impact judgments. The run's one higher-layer identity
supervisor is authoritative.

## Privacy-safe account matching

- Strong evidence includes a public professional-profile link to the account, stable platform
  user ID, verified domain, signed commits, cross-linked package publisher, or multiple
  consistent public profiles.
- Display name, avatar, or name equality alone is weak and cannot confirm an account.
- Use public commit email addresses transiently only when needed for matching; never write them
  to records, snapshots, reports, or CSVs.
- Shared, organization, and bot accounts do not establish personal attribution without an
  authoritative source naming the candidate.
- Organization membership and repository ownership prove neither contribution nor authorship of
  every file.
- Exclude automated dependency updates, generated changes, spam, trivial typo-only activity,
  and identity-ambiguous activity from compatibility output. Retain useful uncertainty in audit
  records.

## Canonical grain and controlled types

Create one row for:

- an owned or maintained project;
- a merged pull request in a third-party project;
- an independently meaningful commit only when no pull request contains it;
- a sustained documentation, review, issue-triage, release, governance, working-group, support,
  or leadership role per project and date range;
- a published package or extension;
- a verified Q&A/community profile summary per platform and reporting period.

Never emit one row per commit when commits belong to a pull request. Never emit one row per
question, answer, reply, or comment.

Use exactly one of:

`Project Creator`, `Maintainer`, `Code Contribution`, `Pull Request`, `Code Review`,
`Documentation`, `Issue or Triage`, `Release Management`, `Package Publisher`,
`Working Group`, `Community Leadership`, `Community Support`, `Community Q&A Summary`,
`Forum Participation Summary`, or `Other`.

Formal standards documents and formally named standards roles must be routed to
`standards-publication-finder`.

## Reconciliation

- Group all related commits under their pull request and retain commit IDs as enriched evidence.
- Treat repository renames and transfers as one project using stable forge repository identity;
  preserve historical names and URLs.
- Merge mirrors and archived copies only when canonical repository identity proves equivalence.
- Keep a fork distinct from upstream when it contains independently attributable work. Record
  upstream lineage without erasing the fork.
- Link package-registry records to source repositories while preserving registry and repository
  URLs, publisher identity, package version lineage, and registry-specific package identity.
- Keep independently meaningful releases, packages, pull requests, and sustained roles separate.
- Aggregate community activity by platform, stable verified account, and reporting period.
  Lifetime is the default canonical period; yearly counts remain enriched evidence unless yearly
  rows were requested.
- Merge renamed profiles only with a stable platform user ID or another strong link.

## Q&A and profile summaries

Prefer one profile summary over downloading every response. Capture only public platform-defined
metrics:

- questions or topics posted;
- answers or responses submitted;
- accepted or endorsed answers;
- comments or replies;
- reputation, points, contribution score, or rank;
- badges, labels, titles, and topic/expertise tags.

Preserve platform meanings and retrieval timestamps for every mutable metric. Individual
response links may be sampled as supporting evidence for identity or quality, but do not create
portfolio rows for each response. Missing, private, deleted, or inaccessible metrics remain
blank and are never estimated. Raw volume is not a quality judgment.

## Impact metrics

Capture directly observed public stars, forks, package downloads, merge status, release
downloads, contributor count, named adoption, governance acceptance, and Q&A metrics. Include
`metrics_retrieved_at`. Do not combine metrics into an opaque score or use them as identity
proof.

## Normalized record examples

Merged pull request:

```json
{
  "artifact_type": "community-contributions",
  "canonical_key": "forge.example|org/project|pull-request|42",
  "title": "Merged pull request: improve retry handling",
  "date": "2025-06-20",
  "fields": {
    "date": "2025-06-20",
    "type": "Pull Request",
    "project": "org/project",
    "organization": "Example Organization",
    "role": "Author",
    "forge": "forge.example",
    "account": "public-account",
    "repository": "org/project",
    "contribution_id": "42",
    "status": "merged",
    "url": "https://forge.example/org/project/pulls/42",
    "package_urls": [],
    "metrics_retrieved_at": "2026-01-15T12:00:00Z"
  },
  "signals": {
    "name": 0.8,
    "affiliation": 0.8,
    "collaborators": 0.7,
    "topic": 0.9,
    "geography": null,
    "timeline": 1.0,
    "creator_role": 1.0,
    "cross_source": 0.8
  },
  "evidence": [
    {
      "evidence_id": "ev-community-001",
      "source_url": "https://forge.example/org/project/pulls/42",
      "retrieved_at": "2026-01-15T12:00:00Z",
      "authority_rank": 1,
      "field": "status",
      "raw_value": "Merged",
      "normalized_value": "merged",
      "extraction_method": "structured"
    }
  ],
  "warnings": []
}
```

Q&A profile summary:

```json
{
  "artifact_type": "community-contributions",
  "canonical_key": "qa.example|stable-user-123|lifetime",
  "title": "Posted 12 questions; answered 48; 9 accepted",
  "date": "",
  "fields": {
    "date": "",
    "type": "Community Q&A Summary",
    "project": "Q&A Example",
    "role": "Contributor",
    "url": "https://qa.example/users/stable-user-123",
    "questions_posted": 12,
    "answers_posted": 48,
    "accepted_answers": 9,
    "comments_or_replies": 31,
    "reputation_or_points": 4200,
    "rank": "",
    "badges": ["Example Gold Badge"],
    "labels": [],
    "topic_tags": ["distributed-systems", "python"],
    "metrics_retrieved_at": "2026-01-15T12:00:00Z"
  },
  "signals": {
    "name": 0.8,
    "affiliation": null,
    "collaborators": null,
    "topic": 0.9,
    "geography": null,
    "timeline": 0.8,
    "creator_role": 1.0,
    "cross_source": 0.8
  },
  "evidence": [],
  "warnings": []
}
```

## Exact output schemas

`community-contributions.csv`:

```text
Contribution,Date,Type,Project,Role,URL
```

`community-contributions.enriched.csv`:

```text
record_id,contribution,type,project,organization,role,forge,account,repository,contribution_id,start_date,end_date,status,technologies,license,url,package_urls,stars,forks,downloads,contributors,metrics_retrieved_at,questions_posted,answers_posted,accepted_answers,comments_or_replies,reputation_or_points,rank,badges,labels,topic_tags,identity_confidence,record_confidence,evidence_coverage,decision,confidence_reasons,source_urls,retrieved_at
```

Use ISO dates when complete, empty strings for unknown values, semicolon-sorted multivalue
fields, stable versioned canonical keys, UTF-8, RFC 4180 quoting, and deterministic ordering.

## Audit and degraded modes

Write workflow evidence to `query-plan.json`, `identity-decisions.jsonl`,
`dedup-decisions.jsonl`, `status-events.jsonl`, `conflicts.jsonl`, `run-report.json`, and
`source-snapshots/`. Audit repository aliases/transfers, fork and upstream decisions, PR/commit
groups, package links, account-match evidence, excluded bot/generated activity, profile summary
periods, sampled responses, and metric timestamps.

- Mark degraded for blocked or rate-limited forge history, unavailable registry/community
  metrics, stale cache, one provider, unresolved account identity, or incomplete rename/fork
  history.
- Distinguish zero contributions from an incomplete search.
- Keep uncertain same-name accounts out of compatibility output and visible in enriched/audit
  artifacts.
- Offline mode replays cached public assertions and reports that current merge states, package
  counts, profile metrics, and repository status were not refreshed.

After supervisor decisions and reconciliation, append normalized JSONL records to the
coordinator's record file. The master skill calls `scripts/run.py`; when invoked alone, this
skill calls it with the validated candidate path, records file, output directory, and
`--consent-confirmed`.

