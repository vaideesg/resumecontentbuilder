from __future__ import annotations

from collections import defaultdict
import json
from typing import Iterable

from .models import ArtifactRecord


PATENT_STATUS_PRECEDENCE = {
    "": 0,
    "Unknown": 0,
    "Application": 1,
    "Published": 1,
    "Published/Pending": 1,
    "Abandoned": 2,
    "Grant": 3,
}


def reconcile_records(records: Iterable[ArtifactRecord]) -> list[ArtifactRecord]:
    groups: dict[tuple[str, str], list[ArtifactRecord]] = defaultdict(list)
    for record in records:
        groups[(record.artifact_type, record.canonical_key)].append(record)

    reconciled: list[ArtifactRecord] = []
    for key in sorted(groups):
        candidates = groups[key]
        if key[0] == "patents":
            winner = max(
                candidates,
                key=lambda item: (
                    PATENT_STATUS_PRECEDENCE.get(str(item.fields.get("type", "")), 0),
                    _deterministic_candidate_key(item),
                ),
            )
        else:
            winner = max(candidates, key=_deterministic_candidate_key)

        merged_evidence = {}
        for candidate in candidates:
            for evidence in candidate.evidence:
                current = merged_evidence.get(evidence.evidence_id)
                if current is None or _evidence_precedence(evidence) > _evidence_precedence(current):
                    merged_evidence[evidence.evidence_id] = evidence
        winner.evidence = [merged_evidence[key] for key in sorted(merged_evidence)]
        winner.warnings = sorted({warning for candidate in candidates for warning in candidate.warnings})
        reconciled.append(winner)

    return reconciled


def _deterministic_candidate_key(record: ArtifactRecord) -> tuple[str, ...]:
    evidence_key = json.dumps(
        [
            {
                "evidence_id": item.evidence_id,
                "authority_rank": item.authority_rank,
                "source_url": item.source_url,
                "retrieved_at": item.retrieved_at,
            }
            for item in sorted(
                record.evidence,
                key=lambda item: (
                    item.evidence_id,
                    item.authority_rank,
                    item.source_url,
                    item.retrieved_at,
                ),
            )
        ],
        sort_keys=True,
        separators=(",", ":"),
    )
    return (
        record.date,
        record.title.casefold(),
        json.dumps(record.fields, sort_keys=True, separators=(",", ":"), default=str),
        json.dumps(record.signals, sort_keys=True, separators=(",", ":"), default=str),
        evidence_key,
    )


def _evidence_precedence(evidence: object) -> tuple[object, ...]:
    return (
        -evidence.authority_rank,
        evidence.retrieved_at,
        evidence.source_url,
        evidence.raw_value,
        evidence.normalized_value,
    )
