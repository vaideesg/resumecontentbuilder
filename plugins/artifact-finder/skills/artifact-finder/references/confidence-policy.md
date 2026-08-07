# Confidence Policy

Confidence scores are transparent heuristics, not calibrated probabilities. The authoritative
higher-layer identity supervisor applies this policy to the complete frozen evidence corpus.
Discovery workers and focused workflows may calculate provisional scores but cannot make final
attribution decisions.

## Measures

Keep these values separate:

- `identity_confidence`: whether the artifact belongs to the configured candidate.
- `record_confidence`: whether normalized artifact fields accurately represent the source.
- `status_confidence`: whether a mutable or legal status is current and authoritative.
- `evidence_coverage`: sum of identity-signal weights for which evidence is observed.
- `confidence_reasons`: concise evidence-linked reasons, including contradictions.

Do not boost identity confidence with popularity, download counts, stars, points, badges, or
other impact metrics.

## Identity scoring

| Signal | Weight |
|---|---:|
| Normalized name | 0.20 |
| Time-aligned affiliation | 0.25 |
| Era-aware collaborator network | 0.25 |
| Topic continuity | 0.15 |
| Public work geography | 0.05 |
| Timeline consistency | 0.04 |
| Creator role or ordering | 0.04 |
| Cross-source corroboration | 0.02 |

Each observed signal is in `[0,1]`; an unavailable signal is `null`, not zero. Compute the
weighted score over observed signals and report coverage separately. Name equality alone is
never sufficient.

Default labels:

- `confirmed`: score >= 0.85, coverage >= 0.60, and at least two non-name corroborators scoring
  >= 0.60.
- `probable`: score >= 0.70 and at least one non-name corroborator scoring >= 0.60.
- `possible`: score >= 0.50 or evidence is too sparse for a stronger decision.
- `unlikely`: score >= 0.30.
- `excluded`: score below 0.30 or direct contradictory evidence establishes an incompatible
  identity cluster.

Missing employer, geography, collaborators, public verification, or registry results is unknown
evidence and cannot independently cause exclusion. Hard exclusion requires direct contradiction
or a confirmed incompatible identity.

Only `confirmed` and `probable` enter compatibility CSVs by default. `possible` remains
`uncertain` unless the request explicitly enables `include_possible`.

## Record and status confidence

Record confidence depends on field-level evidence authority, agreement, extraction reliability,
and canonical-key stability. Search snippets can create candidates but cannot establish final
authorship, validity, delivery, contribution, or status.

Status confidence must account for source authority and retrieval freshness. Only an issuing
authority or equally authoritative first-party system may establish credential revocation,
expiration, pull-request merge state, or another formal current status. Derived date-based
status must cite the source dates and derivation rule.

Use `unknown`, never `invalid`, when:

- a credential is absent from a public registry;
- a verification page is private, blocked, or requires a code;
- expiration or revocation evidence is unavailable;
- a community metric is hidden, deleted, private, or inaccessible;
- a provider could not be searched.

## Supervisor decision contract

Every final decision contains:

```json
{
  "candidate_record_ids": ["candidate-record-001"],
  "decision": "include",
  "identity_confidence": 0.91,
  "confidence_label": "confirmed",
  "record_confidence": 0.96,
  "status_confidence": 0.88,
  "evidence_coverage": 0.76,
  "supporting_evidence_ids": ["ev-001", "ev-002"],
  "contradictory_evidence_ids": [],
  "explanation": "Two non-name public signals corroborate the account and artifact.",
  "assumptions": []
}
```

Allowed decisions are `include`, `exclude`, `uncertain`, `merge`, `split`, and
`targeted_research`. The run has one authoritative supervisor. It may request one bounded
targeted-research round per uncertain cluster, after which it must issue a final decision or
leave the cluster uncertain.

