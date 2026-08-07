# Testing

Run:

```powershell
python -m unittest discover -s plugins\artifact-finder\tests -v
```

Coverage includes:

- Candidate configuration validation
- Identity confidence thresholds
- Patent status reconciliation
- Continuation separation
- Consent enforcement
- Compatibility CSV rendering
- Audit output generation

Live source tests are non-gating because public indexes and engagement metrics change.
