# Backlog: Consent-Based LinkedIn Programmatic Access

## Problem

Public LinkedIn retrieval is incomplete and unreliable for artifact discovery. Automated requests
to the candidate profile and activity pages returned HTTP 999, preventing verification of
candidate-reported articles and current professional identity evidence.

Observed in the August 7, 2026 artifact collection:

- The candidate reports three LinkedIn articles at `linkedin.com/in/vaidees`.
- Direct access to the profile, recent activity, article filter, posts, and publications pages
  returned HTTP 999.
- Three independent searches found no publicly indexed LinkedIn Pulse URLs, cached copies,
  Wayback Machine snapshots, mirrors, or syndicated copies.
- The correct outcome is `unresolved_source_access`, not “zero articles.”
- Public searches found one personal Blogger post, but it is not one of the three LinkedIn
  articles and is not resume-relevant professional writing.
- A similarly named Medium account was determined to be a different person.
- The candidate configuration lists Dell employment, while public secondary evidence suggests
  later Microsoft employment. This needs candidate-approved verification rather than inference.
- LinkedIn employment, collaborator, role, topic, and timeline evidence could improve patent
  inventor disambiguation, but LinkedIn cannot establish patent identifiers, legal status,
  continuity, filing dates, or grant validity.

## Goal

Provide terms-compliant, consent-based access to candidate-owned LinkedIn data so artifact-finder
can verify authored articles and enrich identity evidence used across patents, white papers,
technical talks, certifications, and community contributions.

## Scope

1. Evaluate supported LinkedIn APIs and approved partner access for:
   - the consenting member's profile;
   - authored articles and posts;
   - publication URLs, titles, dates, and visible author attribution;
   - public engagement metrics when the API explicitly exposes them;
   - employment and role history used as identity evidence.
2. Support candidate-provided LinkedIn data exports as the primary fallback when API access is
   unavailable.
3. Support candidate-provided article URLs or exported article HTML/PDF while preserving public
   and private evidence boundaries.
4. Never bypass HTTP 999, login controls, CAPTCHAs, cookies, robots restrictions, rate limits, or
   LinkedIn terms.
5. Do not request, store, or reuse passwords, browser cookies, session tokens, private messages,
   connection lists, contact details, or unrelated activity.
6. Keep LinkedIn evidence secondary for patents:
   - allowed: employer, role, date range, public collaborators, technical topics, and profile
     links for identity corroboration;
   - prohibited: using LinkedIn to establish patent status, inventorship, continuity, filing,
     publication, or grant identifiers without patent-source evidence.
7. Add explicit provider statuses such as `authorized`, `export_imported`, `blocked`,
   `permission_denied`, `rate_limited`, and `not_public`.
8. Cache only the minimum consented artifact metadata with retrieval timestamps and provenance.

## Acceptance Criteria

- The three candidate-reported LinkedIn articles each receive a row-level disposition:
  verified, uncertain, excluded, duplicate/syndicated, or unresolved source access.
- Verified articles include title, canonical URL, publication date, exact author role, category,
  and directly observed metrics where available.
- Missing metrics remain blank and are never inferred.
- A blocked LinkedIn request never becomes a negative finding.
- Candidate-provided exports can be imported without requiring credentials or a live session.
- Imported data is schema-validated, minimized, and restricted to the requested artifact types.
- Employment history from LinkedIn can contribute to patent identity scoring but cannot replace
  official or established-index patent evidence.
- Same-name profiles and accounts require an authoritative profile bridge before attribution.
- The run report distinguishes live API, candidate export, public page, indexed snippet, and
  unavailable evidence.
- Automated tests cover HTTP 999, permission denial, export import, article deduplication,
  missing metrics, employment timeline extraction, and privacy redaction.

## Completion Measure

The work is complete when the system can verify or explicitly account for the three reported
LinkedIn articles through an approved API or candidate-owned export and can safely reuse the
consented employment evidence for identity disambiguation without treating LinkedIn as a patent
authority.
