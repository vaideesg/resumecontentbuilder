# Backlog: Programmatic Patent Source Access and Coverage

## Problem

Patent discovery currently undercounts the candidate's portfolio because authoritative and
secondary patent sources were not exhaustively accessible during automated runs.

Observed in the August 7, 2026 artifact collection:

- The known inventory at `..\agentic_utils\authoringskills\ideas\patents.csv` contains 75 rows,
  75 patent-number values, and 71 unique titles.
- The generated portfolio contains only 22 canonical US application records.
- All 22 generated records match titles in the known inventory; 53 inventory rows were not
  researched or reconciled.
- Justia and USPTO.report returned HTTP 403 to automated requests.
- USPTO.report is a third-party source, not an official USPTO service.
- Official USPTO Patent Center or Open Data APIs were not successfully integrated.
- Google Patents was available, but the run queried only identifiers already present in the
  frozen discovery corpus. It did not perform an exhaustive inventor or baseline-driven search.
- The known CSV's `Application Number` column commonly contains publication numbers such as
  `20190324514`, and sometimes multiple publication numbers, rather than US application serial
  numbers such as `15/960263`.
- Cross-category workers surfaced additional patent evidence, but the master coordinator had to
  correct misclassification from white papers, articles, standards, talks, and community output.

## Goal

Provide reliable, terms-compliant programmatic access to patent bibliographic, application,
continuity, and status data so patent-finder can exhaustively research a supplied inventory and
independently discover the candidate's complete public patent portfolio.

## Scope

1. Integrate official USPTO data services first:
   - Patent Center or supported Patent File Wrapper APIs for application identity, continuity,
     prosecution, and status.
   - Open Data Portal or supported patent-search APIs for grants and pre-grant publications.
   - Bulk data where APIs cannot provide complete, rate-stable coverage.
2. Evaluate documented or licensed programmatic access for Justia and USPTO.report.
   - Do not bypass HTTP 403, CAPTCHAs, authentication, robots restrictions, rate limits, or terms.
   - Treat these providers as secondary discovery/index sources unless they expose authoritative
     upstream evidence.
3. Retain Google Patents as an established-index fallback and cross-source corroborator.
4. Add provider adapters with retries, rate limiting, pagination, caching, source timestamps, and
   explicit blocked/rate-limited states.
5. Support exact lookup by application, publication, and grant identifiers, plus paginated
   inventor-name and assignee searches.
6. Resolve publication numbers from legacy CSVs to application serial numbers before canonical
   application-level reconciliation.
7. Preserve continuations, divisionals, continuations-in-part, reissues, national-stage
   applications, and sibling family applications as distinct records.
8. Reconcile cross-category patent evidence centrally in the master coordinator.

## Acceptance Criteria

- A run using the 75-row known inventory produces a row-level coverage record for every input row.
- Every row is classified as included, uncertain, excluded, duplicate representation, distinct
  related application, or unresolved source access.
- No inventory row disappears during normalization or deduplication.
- Exact identifier gap searches run for every unmapped patent, publication, or application number.
- Provider pagination continues until exhausted or records a precise access/rate-limit failure.
- Reports show inventory rows, unique grant numbers, unique publication numbers, unique
  application serial numbers, and canonical applications separately.
- Differences between the inventory count and portfolio count are fully explained.
- Grant, publication, and application identifiers are not treated as interchangeable.
- Application status and continuity claims use official USPTO evidence when available.
- Justia or USPTO.report failures degrade coverage but do not terminate searches against other
  providers.
- Cross-category patent discoveries appear only in patent output while retaining their original
  source provenance in `cross-category-routing.jsonl`.
- Automated tests cover HTTP 403, rate limiting, pagination, cache replay, identifier conversion,
  continuation preservation, and the 75-row coverage fixture.

## Completion Measure

The work is complete when patent-finder can account for all 75 baseline rows and independently
reproduce the verified canonical application set without relying on manual browsing or silently
accepting a partial broad-name search.
