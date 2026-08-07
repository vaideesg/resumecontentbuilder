# Implementation

## Normalized Record

Each discovery result becomes one JSON object with:

- `artifact_type`
- `canonical_key`
- `title`
- `date`
- Artifact-specific `fields`
- Identity `signals`
- Source `evidence`
- `warnings`

## Reconciliation

Records group by artifact type and canonical key. Patent representations use status precedence
while distinct application keys remain distinct. Other artifact types retain the newest
authoritative representation for the same canonical key.

## Confidence

Identity, record, status, and evidence coverage are independent values. Identity scoring is an
explainable heuristic and not a statistical probability.

## Determinism

Stable record IDs derive from versioned canonical keys. Output timestamps derive from frozen
evidence retrieval timestamps rather than wall-clock execution time.
