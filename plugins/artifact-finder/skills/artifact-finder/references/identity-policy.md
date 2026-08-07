# Identity Policy

The higher-layer identity supervisor is the only stage allowed to make final attribution
decisions. Discovery workers emit evidence, candidate records, and suggested queries only.

Use the shared `candidate.config.json` for identity seeds. Do not embed candidate names,
employers, profiles, or collaborators in skill files.

Score these signals when available:

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

Unknown evidence is not negative evidence. Name equality alone is insufficient. A hard exclusion
requires direct contradictory evidence or an incompatible confirmed identity cluster.

Default labels:

- `confirmed`: score >= 0.85, coverage >= 0.60, and two non-name corroborators.
- `probable`: score >= 0.70 and one non-name corroborator.
- `possible`: score >= 0.50.
- `unlikely`: score >= 0.30.
- `excluded`: lower score or direct contradiction.

Only `confirmed` and `probable` enter compatibility CSVs by default.
