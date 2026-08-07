# Professional Artifact Finder - Master Plan

## 1. Overview

Build a reusable, multi-agent skill that discovers and verifies professional artifacts
created by a consenting person. The initial implementation is `patent-finder`, followed
by specialized discovery pipelines for:

- White papers
- Articles
- Technical talks
- Certifications
- Open-source projects and community contributions
- IETF and other standards publications

The system must produce deterministic CSV outputs, preserve supporting evidence, distinguish
people with similar names, and flag uncertain attribution rather than silently including it.

Each artifact type requires its own source adapters, metadata model, deduplication rules, and
verification policy. A shared higher-layer identity supervisor makes the final attribution
decision across all artifact types.

## 2. Normative Requirements and Provenance

This document is the complete implementation specification. Linked resources are provenance and
test inputs only; an implementer must not need to read another planning document to understand
the required behavior.

- The implementation should use the standard plugin layout:
  `.claude-plugin/plugin.json` plus `skills/<skill>/SKILL.md`.
- All new skill entry files should use the canonical uppercase filename `SKILL.md`.
- The patent CSV contains:
  `Title, Patent Number, Application Number, Type, Filed, Inventors`.
- The repository already supports patent ideation and patent upload, but not retrospective
  discovery of a person's professional body of work.
- The original request backlog is published at
  `https://github.com/vaideesg/resumecontentbuilder/tree/main/backlog`.
- The compatibility schemas from that backlog are reproduced in full in this plan.
- `https://github.com/vaideesg/resumecontentbuilder/blob/main/backlog/data/patents_sample.csv`
  is provenance for the embedded patent fixture below.
- Professional articles include public LinkedIn articles and professional posts. Publicly visible
  impressions must be captured with a retrieval timestamp and never estimated.

## 3. Goals

1. Generate the patent compatibility CSV defined in this plan from public sources.
2. Find name variants and partial-name matches without treating name similarity as proof.
3. Use professional affiliations, co-author networks, dates, topics, and authoritative
   identifiers to disambiguate people.
4. Retain distinct works while collapsing duplicate representations of the same work.
5. Produce compatibility CSVs and richer auditable outputs.
6. Reuse identity evidence across patents, papers, articles, talks, and certifications.
7. Make uncertainty, missing sources, and degraded searches explicit.
8. Capture public engagement metrics, such as article impressions, only when directly visible
   and attributable to the artifact.
9. Restrict article discovery to professional and portfolio-relevant content; do not aggregate
   personal controversy, adverse commentary, or unrelated negative material.
10. Discover open-source projects and community contributions while distinguishing repository
    ownership, code authorship, pull requests, reviews, issues, documentation, package
    maintenance, and community leadership.
11. Discover standards publications and participation, including Internet-Drafts, RFCs,
    specifications, technical reports, working-group documents, and formally recorded editorial
    or contributor roles.

## 4. Non-Goals

- Searching for people without consent or another documented lawful basis.
- Collecting personal contact information, private social-network data, or unrelated personal
  history.
- Treating search snippets as authoritative evidence.
- Claiming that a heuristic confidence score is a calibrated probability.
- Automatically publishing, modifying, or claiming ownership of discovered artifacts.
- Using one generic search prompt as the complete discovery strategy for every artifact type.

## 5. Skill Layout

Create a standard plugin at `./plugins/artifact-finder` with a master skill and focused skills:

```text
plugins/artifact-finder/
|-- .claude-plugin/
|   `-- plugin.json
|-- candidate.config.json
|-- README.md
|-- skills/
|   |-- artifact-finder/
|   |   |-- SKILL.md
|   |   `-- references/
|   |       |-- identity-policy.md
|   |       |-- evidence-policy.md
|   |       |-- confidence-policy.md
|   |       `-- output-contracts.md
|   |-- patent-finder/
|   |   |-- SKILL.md
|   |   `-- references/
|   |       |-- sources.md
|   |       `-- reconciliation-policy.md
|   |-- whitepaper-finder/
|   |   `-- SKILL.md
|   |-- article-finder/
|   |   `-- SKILL.md
|   |-- tech-talk-finder/
|   |   `-- SKILL.md
|   |-- certification-finder/
|   |   `-- SKILL.md
|   |-- standards-publication-finder/
|   |   `-- SKILL.md
|   `-- community-contribution-finder/
|       `-- SKILL.md
|-- scripts/
|   |-- run.py
|   |-- normalize.py
|   |-- identity_graph.py
|   |-- reconcile.py
|   |-- render.py
|   `-- adapters/
`-- tests/
    |-- fixtures/
    `-- test_*.py
```

Each focused command is a real skill within the plugin:

```text
/patent-finder
/whitepaper-finder
/article-finder
/tech-talk-finder
/certification-finder
/standards-publication-finder
/community-contribution-finder
/artifact-finder
```

The plugin manifest should begin with:

```json
{
  "name": "artifact-finder",
  "description": "Discover and verify professional artifacts using multi-agent identity disambiguation.",
  "version": "0.1.0",
  "author": {
    "name": "Resume Content Builder Contributors"
  },
  "keywords": [
    "patents",
    "whitepapers",
    "articles",
    "technical-talks",
    "certifications",
    "standards",
    "ietf",
    "open-source",
    "community-contributions",
    "portfolio"
  ]
}
```

Implement `skills/patent-finder/SKILL.md` first, while keeping shared policies under the master
`skills/artifact-finder/references/` directory.

`candidate.config.json` is the single shared candidate profile for every skill in this plugin.
Focused skills must not embed a person's name, employer, profile URL, account name, or known
collaborator. They load those values from this plugin-root file through the coordinator.

### 5.1 Skill Entry Contract

Every `SKILL.md` must contain:

```yaml
---
name: <skill-name>
description: <when the skill should be invoked and what artifact it produces>
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(*), Task
argument-hint: "candidate_config=<path> consent_confirmed=<true|false> [output_dir=<path>]"
---
```

Each focused skill must:

1. Load shared policies from `skills/artifact-finder/references/`.
2. Validate the common request contract.
3. Run its artifact-specific discovery and reconciliation workflow.
4. Invoke the shared higher-layer identity supervisor.
5. Write its compatibility CSV, enriched CSV, and audit artifacts.

### 5.2 Common Request Contract

```json
{
  "candidate_config": "plugins/artifact-finder/candidate.config.json",
  "consent_confirmed": true,
  "artifact_types": ["patents"],
  "jurisdictions": ["US"],
  "date_from": null,
  "date_to": null,
  "include_possible": false,
  "offline": false,
  "resume_run_id": null,
  "output_dir": "artifact-results"
}
```

Only `candidate_config`, `consent_confirmed`, and `artifact_types` are required. The candidate
configuration supplies the canonical name, variants, employer history, professional profiles,
public accounts, and known collaborators. Empty optional arrays are valid and must not prevent a
run.

### 5.3 Shared Candidate Configuration Contract

The plugin-root `candidate.config.json` uses this schema:

```json
{
  "schema_version": "1.0",
  "candidate": {
    "canonical_name": "<full public name>",
    "known_name_variants": ["<variant>"],
    "employment": [
      {
        "company": "<company>",
        "aliases": ["<legal or historical company name>"],
        "start_date": "YYYY-MM-DD or null",
        "end_date": "YYYY-MM-DD or null"
      }
    ],
    "professional_profiles": [
      {
        "type": "linkedin|github|gitlab|orcid|other",
        "url": "https://...",
        "username": "<optional public username>"
      }
    ],
    "known_collaborators": ["<public professional name>"]
  }
}
```

Rules:

- The file is common to all focused skills inside `plugins/artifact-finder`.
- `canonical_name` is required.
- Variants, employment, profiles, and collaborators are evidence seeds, not proof.
- Skills may enrich the in-memory candidate profile with evidence discovered during a run, but
  they must not silently rewrite the configuration.
- Consent is deliberately not stored in this file; every run still requires
  `consent_confirmed=true`.
- Do not place credentials, private contact information, tokens, cookies, or non-public personal
  data in this file.

Allowed `artifact_types` values are:

- `patents`
- `white-papers`
- `articles`
- `tech-talks`
- `certifications`
- `standards-publications`
- `community-contributions`

## 6. Mandatory Multi-Agent Architecture

### 6.1 Coordinator

- Validates consent and requested scope.
- Loads the request's subject profile and any prior confirmed artifacts supplied by the user or
  cached from an earlier verified run.
- Inventories available tools and source adapters.
- Builds a deterministic task graph.
- Launches at least two discovery workers for each selected artifact type.
- Freezes evidence before final rendering.

### 6.2 Name and Query Planner

Generates:

- Exact full name.
- Reversed name order.
- Initial and abbreviation variants.
- Known spelling and punctuation variants.
- Name plus employer, topic, co-author, location, and date combinations.

It creates search queries but cannot make identity decisions.

### 6.3 Artifact Discovery Workers

Workers are partitioned by source or strategy. They emit evidence assertions rather than final
records. At least two workers must run even when only one provider is available; in that case,
partition by query strategy and disclose that source independence was not achieved.

Every worker output must use this envelope:

```json
{
  "worker_id": "patent-uspto-grants-01",
  "artifact_type": "patent",
  "query_id": "query-...",
  "source": {
    "name": "USPTO",
    "url": "https://...",
    "retrieved_at": "2026-08-07T00:00:00Z",
    "authority_rank": 1
  },
  "retrieval_status": "ok",
  "assertions": [],
  "warnings": []
}
```

Allowed `retrieval_status` values are `ok`, `partial`, `blocked`, `rate_limited`, `timeout`,
`not_found`, and `failed`.

### 6.4 Normalization and Deduplication Agent

- Converts source-specific results into an artifact-specific canonical schema.
- Preserves raw source values.
- Forms candidate duplicate groups.
- Builds person, employer, co-creator, topic, and artifact relationship graphs.

### 6.5 Higher-Layer Identity Supervisor

This agent is mandatory and authoritative.

It receives the complete evidence corpus and issues one of:

- `include`
- `exclude`
- `uncertain`
- `merge`
- `split`
- `targeted_research`

Every decision must contain:

- Candidate record IDs.
- Identity confidence label and heuristic score.
- Evidence coverage.
- Supporting and contradictory evidence IDs.
- Explanation.
- Any assumptions.

Worker recommendations never become final automatically. The supervisor may request one bounded
targeted-research round before making its final decision.

### 6.6 Artifact Reconciliation Agent

Applies artifact-specific version, status, and duplicate rules after identity decisions are
complete.

### 6.7 Renderer and Verifier

- Produces compatibility and enriched CSVs.
- Uses stable ordering and quoting.
- Re-reads generated files.
- Produces a run report and checksum.

## 7. Shared Identity Model

Create a minimal public professional profile containing only evidence needed for attribution:

- Canonical name.
- Known public name variants.
- Employer and role timeline.
- Known co-creators.
- Public professional locations when relevant.
- Technology and subject-area timeline.
- Confirmed public profile identifiers.

Professional-profile URLs from `candidate.config.json` may be used only to confirm public
employer, role, account, and topic timelines. The workflow must not collect connections, contact
details, recommendations, or private activity.

### 7.1 Initial Confidence Signals

| Signal | Initial weight |
|---|---:|
| Normalized name match | 20% |
| Time-aligned employer or publisher affiliation | 25% |
| Era-aware collaborator network | 25% |
| Topic or classification continuity | 15% |
| Public work-related geography | 5% |
| Timeline consistency | 4% |
| Creator ordering or role | 4% |
| Cross-source corroboration | 2% |

These are starting heuristics and must be calibrated with labeled fixtures.

### 7.2 Confidence Labels

- `confirmed`: score at least 85, sufficient evidence coverage, and at least two independent
  non-name corroborators.
- `probable`: 70-84 with at least one non-name corroborator.
- `possible`: 50-69 or insufficient evidence coverage; mandatory review.
- `unlikely`: 30-49.
- `excluded`: below 30 or directly contradictory identity evidence.

Missing evidence is not mismatch evidence. Employer, geography, date, topic, or missing known
collaborators cannot independently cause a hard exclusion.

Store separate measures:

- `identity_confidence`
- `record_confidence`
- `status_confidence`
- `evidence_coverage`
- `confidence_reasons`

### 7.3 Evidence Assertion Contract

Every value used in a final record must be traceable to an assertion:

```json
{
  "evidence_id": "ev-...",
  "candidate_id": "candidate-...",
  "field": "title",
  "raw_value": "Source text",
  "normalized_value": "Normalized value",
  "source_url": "https://...",
  "retrieved_at": "2026-08-07T00:00:00Z",
  "extraction_method": "structured|html|pdf|ocr|manual-rule",
  "authority_rank": 1,
  "confidence": 0.98
}
```

Source authority ranks:

1. Issuer, patent office, publisher, conference organizer, or credential authority.
2. Established index or repository that links to the primary source.
3. Employer biography or verified professional profile.
4. General web result or aggregator.
5. Search snippet.

Rank 5 can create a discovery candidate but cannot establish final authorship, identity, legal
status, delivery, or certification validity.

## 8. Artifact-Specific Discovery Plans

## 8.1 Patents

### Sources

1. USPTO grant and pre-grant publication data.
2. USPTO application status and continuity data.
3. Optional EPO OPS, WIPO, or Lens family corroboration.
4. Search engines and aggregators only for discovery.

Live endpoints, authentication, terms, and rate limits must be verified during implementation.

### Canonical Grain

One row per jurisdictional non-provisional application.

### Reconciliation Rules

- Merge publication and grant representations only when authoritative identifiers link them to
  the same application.
- Preserve continuations, divisionals, continuation-in-part applications, reissues, and national
  stage applications as separate rows.
- Link related applications through continuity and family fields.
- Grant supersedes Published for the same application.
- Authoritative abandonment supersedes Published/Pending for that application only.
- Never collapse by title alone.

### Compatibility Output

```text
Title,Patent Number,Application Number,Type,Filed,Inventors
```

Also produce `patents.enriched.csv` with canonical application, publication and grant numbers,
assignee, continuity, family, source evidence, and confidence fields.

The compatibility `Type` vocabulary is:

- `Grant`
- `Application`
- `Abandoned`

The embedded golden contract fixture is:

```csv
"Title","Patent Number","Application Number","Type","Filed","Inventors"
"Example information-handling-system invention","12345678","20240001234","Grant","January 15, 2022","Example Inventor, Candidate Name"
```

The skill must discover the complete patent dataset from authoritative sources rather than
depending on a pre-existing complete CSV.

## 8.2 White Papers

White papers are commonly duplicated across corporate sites, PDF repositories, conference pages,
and content-delivery networks. Authorship may appear only inside the PDF.

### Sources

1. Employer publication and research portals.
2. Institutional repositories and digital libraries.
3. Public PDF searches restricted by employer and topic.
4. Conference or standards-body resource libraries.
5. DOI/Crossref records when a DOI exists.

### Discovery Strategy

- Search exact and variant names with employer and technical-topic terms.
- Search PDFs by author lines, acknowledgements, and metadata.
- Extract title page, publication date, organization, authors, abstract, document identifier,
  revision, and canonical URL.
- Confirm that the person's role is author or contributor, not merely quoted or acknowledged.

### Canonical Grain

One row per intellectual work and major published edition.

### Deduplication

- Use DOI or publisher document ID when available.
- Otherwise use normalized title, author set, publisher, publication date, and PDF content hash.
- Treat format mirrors as one work.
- Keep materially revised editions separately and link them with `supersedes`.

### Key Confidence Signals

- Author byline inside the document.
- Employer affiliation at publication time.
- Publisher-controlled page.
- Co-author overlap.
- Topic continuity.
- PDF metadata alone is weak evidence and must not establish authorship.

### Compatibility Output

```text
Title,Published Date,Type,Domain,Website
```

`Website` is a human-readable publisher/source label, such as `Publisher White Paper`. The enriched output additionally
stores canonical URL, authors, publisher, revision, document ID, content hash, evidence, and
confidence.

The embedded white-paper positive fixture is:

```csv
"Title","Published Date","Type","Domain","Website"
"Example systems-management scalability paper","July 2021","Technical White Paper","Systems Management","Publisher White Paper"
```

## 8.3 Articles

Articles include technical blogs, magazine contributions, research articles, newsletters, guest
posts, public LinkedIn articles, and professional LinkedIn posts. Search results often confuse
authors with people mentioned in the text.

### Sources

1. Author profile pages on publisher-controlled sites.
2. Employer engineering blogs and official publications.
3. DOI/Crossref, ORCID, Semantic Scholar, or scholarly indexes when applicable.
4. Reputable magazines and conference publications.
5. Personal sites only when identity ownership can be corroborated.

### Discovery Strategy

- Search by exact byline plus employer and topic.
- Follow author archive/profile pages before broad page searches.
- Distinguish `author`, `editor`, `reviewer`, `interviewee`, and `mentioned_person`.
- Capture canonical URL, publication date, publisher, article type, co-authors, DOI, and archive
  URL.
- Search LinkedIn public article/activity pages when permitted by access controls and terms.
- Capture impressions, views, reactions, comments, and reposts only when explicitly visible.
- Store the metric value with its retrieval timestamp because engagement metrics change.
- Never infer impressions from reactions or follower counts.

### Canonical Grain

One row per article.

### Deduplication

- Prefer DOI or publisher canonical URL.
- Merge syndicated copies and reposts while preserving all URLs.
- Keep translations and materially revised editions linked but distinct.
- Do not merge articles solely because titles are similar.

### Key Confidence Signals

- Structured byline or publisher author profile.
- DOI/ORCID linkage.
- Employer and co-author consistency.
- Topic and timeline continuity.
- Pages that only mention the person are exclusions.

### Professional Content Categories

Use a controlled, resume-oriented taxonomy:

- `Technical`
- `Architecture`
- `Engineering Leadership`
- `Innovation`
- `Career Development`
- `Mentoring`
- `Product or Industry Insight`
- `Event or Community`
- `Other Professional`

Exclude personal disputes, political content, allegations, adverse commentary, and content where
the person is merely discussed. "Avoid negative content" is implemented as a professional-scope
filter, not as alteration of an author's actual article.

### Compatibility Output

```text
Title,Published Date,Type,Category,Website,Impressions
```

The enriched output additionally stores author role, publisher, canonical URL, co-authors,
engagement metric type, metric retrieval date, archive URL, evidence, and confidence.

## 8.4 Technical Talks

Talks can have multiple event pages, slide decks, recordings, agendas, and repeated deliveries.
Speaker attribution and event occurrence both require verification.

### Sources

1. Official conference and meetup schedules.
2. Employer event pages.
3. Public video platforms and podcast feeds.
4. Slide repositories.
5. Event archives and speaker profile pages.

### Discovery Strategy

- Search name variants with `speaker`, `session`, `conference`, `webinar`, `podcast`, and known
  topics.
- Search employer plus likely event series.
- Match event page, recording, slides, and speaker biography.
- Capture event, session title, delivery date, venue, location/online status, role, co-speakers,
  recording, slides, and duration.

### Canonical Grain

One row per delivered session.

The same talk delivered at multiple events remains multiple rows linked through a
`talk_series_id`.

### Deduplication

- Merge event-page, recording, and slide representations of one delivery.
- Use event name, session title, date, speaker set, and recording metadata.
- Keep rehearsals, trailers, playlists, and promotional clips out of the final dataset.

### Key Confidence Signals

- Official event schedule naming the speaker.
- Video description plus visible/on-audio speaker identity.
- Speaker profile and employer alignment.
- Co-speaker network.
- Slide metadata alone is insufficient.

### Compatibility Output

```text
Talk,Published Date,Type,Where
```

`Published Date` represents the delivery date when known; otherwise it uses the earliest
authoritative publication or upload date.
The enriched output distinguishes delivery date, upload/publication date, event, organizer,
venue, speaker role, recording, slides, co-speakers, evidence, and confidence.

## 8.5 Certifications

Certifications require a privacy-sensitive and issuer-specific workflow. Some credentials are
publicly verifiable while others are private or protected by verification codes.

### Sources

1. Issuer-controlled public credential pages.
2. Public digital credential platforms such as Credly.
3. Public professional-profile certification entries.
4. Employer biography pages as secondary corroboration.
5. User-provided certificate files or verification links.

### Discovery Strategy

- Start from issuer names and known certification families rather than broad name-only searches.
- Prefer public issuer verification endpoints.
- Ask the user to provide private verification links or certificate files when public discovery
  is unavailable.
- Capture credential name, issuer, level, issue date, expiration date, credential ID only when
  already public, status, and verification URL.

### Canonical Grain

One row per issued credential instance.

### Deduplication and Status

- Use issuer plus public credential ID when available.
- Otherwise use normalized credential name, issuer, issue date, and level.
- Preserve renewals as separate instances linked through `renews`.
- Derive `active`, `expired`, `revoked`, or `unknown` only from issuer evidence and dates.

### Privacy Rules

- Never guess credential IDs.
- Never bypass login or verification controls.
- Do not publish certificate numbers that were supplied privately.
- Absence from a public registry does not prove that a certification does not exist.

### Compatibility Output

```text
Certification,Published Date,Type,Where
```

`Published Date` represents issue date when known. The enriched output distinguishes issue,
expiration, renewal and verification dates, issuer, credential platform, credential level,
current status, public verification URL, evidence, and confidence.

## 8.6 Open-Source Projects and Community Contributions

This workflow discovers publicly attributable contributions to software, documentation,
standards, technical communities, and public engineering initiatives. A repository appearing on
a person's profile is not sufficient evidence that the person created or materially contributed
to it.

### Sources

1. GitHub, GitLab, or other public forge user and organization profiles.
2. Repository commit, pull-request, review, issue, release, and contributor histories.
3. Package registries such as npm, PyPI, NuGet, Maven Central, crates.io, and Go module indexes.
4. Project-maintainer pages, governance files, release notes, and contributor documentation.
5. Standards bodies, technical working groups, foundations, community event sites, and public
   project acknowledgements.
6. Public technical Q&A and discussion communities such as Stack Overflow, Microsoft Q&A,
   GitHub Discussions, project forums, vendor communities, and standards mailing-list archives.
7. Public professional profiles as discovery evidence only.

### Discovery Strategy

- Resolve public forge identities from profile links, verified domains, commit identities, and
  cross-linked professional profiles.
- Search repositories owned by the subject and repositories where the subject has authored
  commits, opened or merged pull requests, performed reviews, filed substantive issues, written
  documentation, published releases, or held a documented maintainer role.
- Search package registries for packages linked to verified forge identities or publisher
  accounts.
- Search standards, foundation, working-group, and community pages for named roles and published
  contributions.
- Resolve public Q&A/community profiles and retrieve aggregate participation data such as
  questions posted, answers submitted, accepted answers, reputation or points, badges, labels,
  ranks, and primary topic tags.
- Capture contribution type, project, organization, role, date range, contribution URLs,
  technologies, license, and public impact metrics.
- Exclude automated dependency updates, generated commits, trivial typo-only changes, spam,
  duplicated mirrors, and activity where identity cannot be corroborated.
- Do not create a portfolio row for every forum reply or answer. Preserve individual response
  links only as sampled or supporting evidence when needed for identity or quality verification.

### Canonical Grain

Use one row per meaningful contribution unit:

- One row per owned or maintained project.
- One row per merged pull request in a third-party project.
- One row per independently meaningful commit when no pull request exists.
- One row per sustained documentation, review, issue-triage, release-management, governance, or
  community-leadership role per project and date range.
- One row per published package or extension.
- One summary row per verified Q&A/community profile and reporting period. The default reporting
  period is the profile's lifetime totals; optionally add yearly summary rows when reliable
  dated activity is available.

Do not create one row for every commit when multiple commits belong to the same pull request.
Do not create one row for every question, answer, reply, or comment.

### Contribution Types

Use this controlled vocabulary:

- `Project Creator`
- `Maintainer`
- `Code Contribution`
- `Pull Request`
- `Code Review`
- `Documentation`
- `Issue or Triage`
- `Release Management`
- `Package Publisher`
- `Working Group`
- `Community Leadership`
- `Community Support`
- `Community Q&A Summary`
- `Forum Participation Summary`
- `Other`

### Attribution and Identity Rules

- A verified forge account linked from a public professional profile is strong identity evidence.
- Matching display names without account linkage are weak evidence.
- Commit email addresses must not be exported. They may be used transiently for matching only
  when already public in commit metadata.
- A contribution attributed only through a shared or bot account is excluded unless another
  authoritative source names the subject.
- Repository ownership proves control of the repository, not authorship of every file or commit.
- Organization membership is insufficient without contribution or role evidence.
- Co-contributor networks, employer timing, technology continuity, signed commits, profile links,
  and package-publisher identities provide corroboration.
- Q&A profile identity should be corroborated through profile links, verified forge identities,
  employer/topic continuity, or multiple consistent public profiles. A matching display name and
  avatar alone are insufficient.

### Deduplication

- Group commits under their pull request when a pull-request relationship exists.
- Merge forge mirrors and archived repository copies using canonical repository identity.
- Merge package-registry records with their source repository while preserving both URLs.
- Keep separate releases, packages, pull requests, and sustained roles when they represent
  independently meaningful work.
- Aggregate Q&A activity by platform, verified account, and reporting period.
- If a platform exposes both lifetime and yearly counts, keep the lifetime summary as canonical
  and store yearly values in enriched evidence unless yearly rows are explicitly requested.
- Merge renamed community profiles only when the platform exposes a stable user ID or another
  strong identity link.
- Treat repository renames or transfers as the same project and preserve historical names.
- Do not merge forks with their upstream repository when the fork contains independently
  attributable work.

### Impact Metrics

Capture only public, directly observed values with retrieval timestamps:

- Repository stars and forks.
- Package downloads when the registry exposes them.
- Pull-request merge status.
- Release/download counts.
- Number of distinct contributors.
- Adoption by named public projects.
- Standards or governance acceptance status.
- Questions or topics posted.
- Answers or responses submitted.
- Accepted or endorsed answers.
- Public reputation, points, rank, or contribution score.
- Public badges, labels, titles, and expertise tags.

Do not combine these into an opaque impact score. Metrics are mutable context, not proof of
contribution quality.

For Q&A summaries:

- Preserve the platform's own metric names and meanings.
- Store points, reputation, ranks, badges, and labels only when publicly visible.
- Record the metric retrieval timestamp.
- Do not estimate deleted, private, or inaccessible activity.
- Do not use raw posting volume alone as a quality judgment.
- Prefer accepted answers, endorsements, useful votes, badges, and recognized topic labels as
  evidence of community credibility.

### Compatibility Output

```text
Contribution,Date,Type,Project,Role,URL
```

The enriched output distinguishes forge identity, organization, repository, contribution ID,
start and end dates, status, technologies, license, impact metrics and retrieval dates,
identity confidence, record confidence, evidence, and reasons. Q&A summary rows use the platform
name as `Project`, the verified account's public role or rank as `Role`, and a summary such as
`Posted 24 questions; answered 86; 19 accepted` as `Contribution`.

Formal standards documents and formally named standards roles must be routed to the
`standards-publication-finder`. The community workflow retains only informal community support or
participation that does not qualify as a standards publication or formal standards role.

## 8.7 IETF and Standards Publications

This workflow discovers formally published or archived standards work. It distinguishes document
authorship and editorship from working-group membership, mailing-list participation, meeting
attendance, acknowledgements, and implementation experience.

### Sources

1. IETF Datatracker for people, Internet-Drafts, working groups, document history, roles, and
   status.
2. RFC Editor for published RFC metadata and canonical document status.
3. IETF working-group archives and proceedings as supporting evidence.
4. W3C specifications, working drafts, recommendations, group pages, and contributor records.
5. OASIS standards, committee specifications, and technical committee pages.
6. IEEE Standards Association public metadata and working-group pages.
7. ISO/IEC, Ecma, CNCF, OpenSSF, Linux Foundation, and other standards or specification bodies
   where public contributor metadata is available.
8. Employer or professional profiles only as secondary corroboration.

### Discovery Strategy

- Search canonical and variant names in standards-body person, author, editor, contributor, and
  acknowledgement fields.
- Search known employer, email-domain history, working groups, technical topics, co-authors, and
  date ranges.
- For IETF, follow the progression from individual or working-group Internet-Draft versions to
  an adopted draft, approved document, and RFC when applicable.
- Capture document title, stable identifier, version, publication date, status, standards body,
  working group or committee, role, co-authors/editors, canonical URL, predecessor/successor
  relationships, and obsoletes/updates relationships.
- Record participation such as chair, secretary, document shepherd, designated expert, reviewer,
  or named contributor separately from document authorship.
- Treat mailing-list messages, meeting attendance, and repository commits as supporting evidence
  unless they establish a documented standards role or substantive named contribution.

### Canonical Grain

- One row per standards document lineage.
- IETF Internet-Draft revisions with the same draft name form one lineage rather than one row per
  revision.
- When an Internet-Draft becomes an RFC, preserve the draft lineage and RFC identifiers in one
  canonical row and set the latest publication state to `RFC`.
- Keep independently published successor, replacement, update, or extension documents separate
  and link them through relationship fields.
- One separate row per formally documented non-author role when it represents meaningful
  standards leadership or contribution.

### Publication Types

- `Internet-Draft`
- `Working Group Draft`
- `RFC`
- `Standard`
- `Proposed Standard`
- `Best Current Practice`
- `Informational`
- `Experimental`
- `Specification`
- `Recommendation`
- `Technical Report`
- `Committee Specification`
- `Standards Leadership`
- `Standards Contribution`

### Status Reconciliation

For IETF document lineages, use the latest authoritative state:

1. `RFC` when published by the RFC Editor.
2. `Approved` when approved but not yet published as an RFC.
3. `Active Draft` when the latest draft remains active.
4. `Expired Draft` when the draft expired without a superseding active version.
5. `Replaced` when another document explicitly replaces or supersedes it.
6. `Withdrawn` when the standards body records withdrawal.

An expired draft must not be treated as failed or abandoned when it led to an RFC or replacement
document. Preserve the complete status history in enriched output.

### Identity and Role Rules

- Exact author/editor metadata from the standards body is strong evidence.
- Stable person IDs, Datatracker profiles, ORCID, verified profile links, and consistent public
  email-domain history are corroborating identity signals.
- Email addresses may be used transiently for matching but must not appear in output unless the
  standards publication itself requires the address as part of its canonical citation.
- Acknowledgement alone does not establish authorship; record it as `Standards Contribution`
  only when the contribution is named and materially described.
- Working-group membership or mailing-list activity alone does not establish document
  contribution.
- Co-author networks, employer timeline, topic continuity, and document history help resolve
  abbreviated or reordered names.

### Deduplication

- Group Internet-Draft revisions by stable draft name.
- Link drafts to RFCs using authoritative Datatracker/RFC Editor relationships.
- Merge HTML, text, XML, PDF, and repository representations of the same document.
- Preserve errata as status/evidence records unless the person is explicitly named as an errata
  reporter or verifier and that role is requested.
- Keep translated, updated, obsoleting, and obsoleted standards as distinct linked documents.

### Compatibility Output

```text
Title,Published Date,Type,Standards Body,Working Group,Role,Identifier,Status,URL
```

The enriched output adds draft lineage, revision history, RFC or specification identifiers,
authors/editors, committee, document relationships, status history, identity confidence,
record/status confidence, evidence, and retrieval timestamps.

## 9. Shared Output Contract

Create one portfolio index:

```text
artifact_type,title,date,organization,creators,status,canonical_url,
identity_confidence,record_confidence,status_confidence,evidence_coverage,
confidence_reasons,source_urls
```

Also create artifact-specific compatibility and enriched CSVs:

```text
patents.csv
patents.enriched.csv
white-papers.csv
articles.csv
tech-talks.csv
certifications.csv
standards-publications.csv
community-contributions.csv
professional-artifacts.csv
```

Compatibility headers must exactly follow these contracts:

| Artifact | Compatibility columns |
|---|---|
| Patent | `Title, Patent Number, Application Number, Type, Filed, Inventors` |
| White paper | `Title, Published Date, Type, Domain, Website` |
| Article | `Title, Published Date, Type, Category, Website, Impressions` |
| Technical talk | `Talk, Published Date, Type, Where` |
| Certification | `Certification, Published Date, Type, Where` |
| Standards publication | `Title, Published Date, Type, Standards Body, Working Group, Role, Identifier, Status, URL` |
| Community contribution | `Contribution, Date, Type, Project, Role, URL` |

The compatibility schemas in this table are normative; implementations must not require the
original backlog files.

### 9.1 Exact Enriched Schemas

`patents.enriched.csv`:

```text
record_id,family_id,jurisdiction,application_number,publication_numbers,
grant_numbers,title,filing_date,current_status,status_effective_date,inventors,
assignees,continuity_type,parent_application,identity_confidence,record_confidence,
status_confidence,evidence_coverage,decision,confidence_reasons,source_urls,retrieved_at
```

`white-papers.enriched.csv`:

```text
record_id,title,published_date,type,domain,website,publisher,authors,document_id,
doi,revision,canonical_url,content_hash,identity_confidence,record_confidence,
evidence_coverage,decision,confidence_reasons,source_urls,retrieved_at
```

`articles.enriched.csv`:

```text
record_id,title,published_date,type,category,website,publisher,author_role,
co_authors,doi,canonical_url,archive_url,impressions,views,reactions,comments,
reposts,metrics_retrieved_at,identity_confidence,record_confidence,
evidence_coverage,decision,confidence_reasons,source_urls,retrieved_at
```

`tech-talks.enriched.csv`:

```text
record_id,talk_series_id,title,type,delivery_date,publication_date,event,
organizer,where,venue_mode,speaker_role,co_speakers,recording_url,slides_url,
duration_minutes,identity_confidence,record_confidence,evidence_coverage,
decision,confidence_reasons,source_urls,retrieved_at
```

`certifications.enriched.csv`:

```text
record_id,certification,type,issuer,where,level,issue_date,expiration_date,
renewal_date,status,public_credential_id,verification_url,identity_confidence,
record_confidence,status_confidence,evidence_coverage,decision,
confidence_reasons,source_urls,retrieved_at
```

`community-contributions.enriched.csv`:

```text
record_id,contribution,type,project,organization,role,forge,account,
repository,contribution_id,start_date,end_date,status,technologies,license,url,
package_urls,stars,forks,downloads,contributors,metrics_retrieved_at,
questions_posted,answers_posted,accepted_answers,comments_or_replies,
reputation_or_points,rank,badges,labels,topic_tags,
identity_confidence,record_confidence,evidence_coverage,decision,
confidence_reasons,source_urls,retrieved_at
```

`standards-publications.enriched.csv`:

```text
record_id,lineage_id,title,published_date,type,standards_body,working_group,
committee,role,identifier,status,version,authors_editors,canonical_url,
predecessor_ids,successor_ids,updates_ids,updated_by_ids,obsoletes_ids,
obsoleted_by_ids,status_history,identity_confidence,record_confidence,
status_confidence,evidence_coverage,decision,confidence_reasons,source_urls,
retrieved_at
```

All compatibility CSVs:

- Use UTF-8 encoding.
- Use RFC 4180 quoting.
- Use an empty string for unknown values.
- Preserve human-readable dates in the compatibility file.
- Sort newest date first, then normalized title, then stable `record_id`.

All enriched CSVs:

- Use ISO `YYYY-MM-DD` dates where a complete date is known.
- Preserve partial dates in a separate raw evidence assertion.
- Sort multivalue fields lexicographically and join them with semicolons.
- Use stable IDs derived from versioned canonical keys.

Audit artifacts:

```text
run-manifest.json
query-plan.json
identity-decisions.jsonl
dedup-decisions.jsonl
status-events.jsonl
conflicts.jsonl
run-report.json
source-snapshots/
```

## 10. Invocation Examples

```text
/patent-finder candidate_config="plugins/artifact-finder/candidate.config.json" \
  consent_confirmed=true

/artifact-finder candidate_config="plugins/artifact-finder/candidate.config.json" \
  consent_confirmed=true \
  types="patents,white-papers,articles,tech-talks,certifications,standards-publications,community-contributions"

/standards-publication-finder candidate_config="plugins/artifact-finder/candidate.config.json" \
  consent_confirmed=true \
  standards_bodies="IETF,W3C,OASIS,IEEE"

/community-contribution-finder candidate_config="plugins/artifact-finder/candidate.config.json" \
  consent_confirmed=true

/artifact-finder resume=<run-id> offline=true
```

Defaults:

- Jurisdiction: US for patents.
- Include `confirmed` and `probable`.
- Keep `possible` records only in enriched review output.
- Use public sources and existing cache.
- Do not require LinkedIn.

## 11. Failure and Degraded Modes

Run states:

- `COMPLETE`
- `COMPLETE_DEGRADED`
- `PARTIAL`
- `FAILED`

Hard failures:

- Consent not confirmed.
- No authoritative source and no usable cache.
- Corrupt checkpoints that cannot be safely rebuilt.
- Output schema or verification failure.

Degraded completion:

- Optional source unavailable.
- Source blocks automation.
- Rate-limited partial coverage.
- Status evidence is stale.
- Identity or duplicate grouping remains unresolved.
- Only one independent source provider was available.

The skill must distinguish `valid search with no results` from `search could not be completed`.

## 12. Implementation Phases

### Phase 1 - Shared Foundation

- Create skill skeleton and schemas.
- Implement consent validation.
- Implement run manifest, evidence store, caching, retries, and deterministic rendering.
- Implement the shared identity supervisor.

### Phase 2 - Patent Finder

- Implement USPTO adapters.
- Normalize application, publication, and grant identifiers.
- Build continuity and family graphs.
- Reconcile Grant, Published/Pending, and Abandoned states.
- Generate the complete patent compatibility CSV and enriched output from authoritative sources.

### Phase 3 - White Papers and Articles

- Implement PDF extraction, DOI/Crossref, publisher-page, canonical-URL, and syndication rules.
- Add author-role classification.
- Add LinkedIn/public article discovery where permitted.
- Add mutable engagement metrics with retrieval timestamps.
- Add the professional-content category classifier and exclusion policy.

### Phase 4 - Technical Talks

- Implement event, video, podcast, and slide adapters.
- Add one-delivery-per-row reconciliation and recurring-talk linkage.

### Phase 5 - Certifications

- Implement issuer and credential-platform adapters.
- Add privacy gates, renewal linkage, and expiration status.

### Phase 6 - IETF and Standards Publications

- Implement IETF Datatracker and RFC Editor adapters first.
- Implement draft-lineage, revision, adoption, approval, RFC publication, replacement, update,
  and obsolescence reconciliation.
- Add W3C, OASIS, IEEE, ISO/IEC, and other standards-body adapters incrementally.
- Implement author, editor, chair, shepherd, reviewer, and named-contributor role distinctions.

### Phase 7 - Open Source and Community Contributions

- Implement forge, repository-history, package-registry, and community-site adapters.
- Implement Q&A/community profile adapters that prefer aggregate public profile metrics over
  downloading every response.
- Resolve verified public accounts and commit identities without exporting email addresses.
- Implement pull-request/commit grouping, repository rename and mirror reconciliation, package
  linkage, Q&A profile summaries, role classification, and mutable impact metrics.

### Phase 8 - Unified Portfolio

- Merge confirmed artifact indexes without losing artifact-specific metadata.
- Add cross-artifact identity reinforcement.
- Add summary reporting by employer, year, topic, and artifact type.

### Phase 9 - Calibration

- Label known positive, negative, and uncertain fixtures.
- Measure precision by artifact type and confidence tier.
- Adjust thresholds and signal weights.
- Only describe scores as probabilities if empirical calibration supports that claim.

## 13. Testing Strategy

### Shared Tests

- Name variants and reordered names.
- Same-name different-person clusters.
- Employer transitions.
- Co-creator network changes.
- Unknown evidence does not become negative evidence.
- Randomized worker completion produces byte-identical output.
- Prompt-injection text in source pages is treated as data.
- Resume and offline replay reproduce the same result.

### Patent Fixtures

- Publication and grant for one application collapse.
- Same-title continuations remain separate.
- Abandoned parent does not mark a continuation abandoned.
- Same-title candidate groups receive explicit merge or split decisions.

### White-Paper Fixtures

- Publisher page and mirrored PDF merge.
- Revised edition remains separate.
- Acknowledged person is not classified as author.

### Article Fixtures

- Canonical article and syndicated copy merge.
- Interview subject is not classified as author.
- DOI and author-profile evidence reinforce attribution.
- Visible LinkedIn impressions are captured with retrieval date.
- Missing impressions remain blank rather than estimated.
- Non-professional or adverse third-party content is excluded.

### Talk Fixtures

- Event page, recording, and slides merge into one delivery.
- Repeated delivery remains separate.
- Playlist and promotional clip are excluded.

### Certification Fixtures

- Renewal remains separate but linked.
- Expiration derives from issuer evidence.
- Missing public verification produces `unknown`, not `invalid`.

### Community-Contribution Fixtures

- Multiple commits in one pull request collapse into one contribution row.
- A repository rename remains one project.
- A fork with independent work remains distinct from upstream.
- Organization membership without contribution evidence is excluded.
- Bot-authored and generated changes are excluded.
- Package registry and source repository records link without losing either URL.
- Mutable stars, forks, and downloads include retrieval timestamps.
- A same-name forge account without corroboration remains uncertain.
- A Q&A profile produces one aggregate summary instead of one row per answer.
- Public answers, accepted answers, reputation, points, badges, labels, rank, and topic tags are
  captured with their platform-specific meanings and retrieval timestamps.
- Missing or private Q&A metrics remain blank rather than estimated.

### Standards-Publication Fixtures

- Multiple revisions of one Internet-Draft form one lineage.
- An Internet-Draft that became an RFC has latest status `RFC`, not `Expired Draft`.
- A replacement draft links to but does not overwrite its predecessor.
- HTML, text, XML, and PDF forms merge into one document record.
- An acknowledged person is not classified as an author.
- Working-group membership alone does not create a publication row.
- Chair, shepherd, editor, reviewer, and author roles remain distinct.
- Same-name authors in unrelated standards groups remain separate until identity is corroborated.

## 14. Acceptance Criteria

- Every run uses multiple discovery agents.
- Every included artifact has a final higher-layer supervisor decision.
- Every identity, duplicate, and status decision references evidence.
- Artifact-specific workflows use different source and reconciliation strategies.
- All compatibility CSVs match the contracts in Section 9 exactly.
- Compatibility CSVs remain usable without losing enriched evidence.
- The patent workflow generates the six-column patent contract and matches the embedded fixture.
- The white-paper workflow matches the embedded candidate-neutral positive fixture.
- Article impressions are never inferred and always include a retrieval timestamp in enriched
  output.
- Suspicious matches remain visible with confidence and reasons.
- No distinct continuation, revised publication, repeated talk, or renewed certification is
  incorrectly collapsed.
- Open-source rows distinguish ownership, authorship, maintenance, review, documentation, and
  community roles.
- Community Q&A activity is summarized by verified platform profile and reporting period rather
  than expanded into every individual response.
- Standards outputs distinguish draft lineage, current publication status, document authorship,
  editorship, leadership, and named contribution roles.
- IETF drafts that become RFCs are reconciled into one lineage without losing revision history.
- Commit email addresses and other unnecessary personal identifiers never appear in outputs.
- Public impact metrics are evidence-linked, timestamped, and never treated as identity proof.
- Source failures and reduced coverage are explicit.
- Identical cached evidence produces deterministic output.

## 15. Resolved Design Decisions and Defaults

- The master `artifact-finder` skill orchestrates the focused skills; it does not replace them.
- Patent scope starts with US records. International sources are optional corroboration until a
  later release adds first-class international output.
- Compatibility CSV order is deterministic but need not reproduce historical row order.
- Certification support begins with generic issuer-controlled verification pages, Credly, and
  user-provided public verification URLs. Add issuer-specific adapters incrementally.
- Scholarly papers, technical blogs, newsletters, and professional LinkedIn content share the
  article dataset and are distinguished by `Type`.
- LinkedIn long-form articles and professional posts are included. Personal posts and third-party
  posts merely mentioning the subject are excluded.
- Open-source scope includes public code, documentation, packages, reviews, issue triage,
  informal working-group support, documented community leadership, and summarized Q&A/forum
  participation. Formal standards documents and roles use the standards-publication workflow.
- Standards publications are a first-class artifact type. IETF support is implemented first,
  followed by W3C, OASIS, IEEE, ISO/IEC, and other bodies with public metadata.
- Trivial, automated, generated, or identity-ambiguous activity is excluded from compatibility
  output and retained only in review artifacts when useful.
- `include_possible` defaults to `false`; possible matches remain in enriched review artifacts.
- One bounded targeted-research round is allowed per uncertain identity cluster.
- This document is authoritative when a linked provenance file differs from the requirements
  stated here.
