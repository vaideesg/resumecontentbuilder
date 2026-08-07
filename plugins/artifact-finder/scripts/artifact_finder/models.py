from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


ARTIFACT_TYPES = {
    "patents",
    "white-papers",
    "articles",
    "tech-talks",
    "certifications",
    "standards-publications",
    "community-contributions",
}


@dataclass(frozen=True)
class SourceEvidence:
    evidence_id: str
    source_url: str
    retrieved_at: str
    authority_rank: int
    field: str = ""
    raw_value: str = ""
    normalized_value: str = ""
    extraction_method: str = "structured"

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "SourceEvidence":
        if not isinstance(value, dict):
            raise ValueError("Each evidence entry must be an object")
        return cls(
            evidence_id=str(value.get("evidence_id", "")),
            source_url=str(value.get("source_url", "")),
            retrieved_at=str(value.get("retrieved_at", "")),
            authority_rank=int(value.get("authority_rank", 5)),
            field=str(value.get("field", "")),
            raw_value=str(value.get("raw_value", "")),
            normalized_value=str(value.get("normalized_value", "")),
            extraction_method=str(value.get("extraction_method", "structured")),
        )


@dataclass
class ArtifactRecord:
    artifact_type: str
    canonical_key: str
    title: str
    date: str = ""
    fields: dict[str, Any] = field(default_factory=dict)
    signals: dict[str, float | None] = field(default_factory=dict)
    evidence: list[SourceEvidence] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ArtifactRecord":
        if not isinstance(value, dict):
            raise ValueError("Each record must be an object")
        artifact_type = str(value.get("artifact_type", ""))
        if artifact_type not in ARTIFACT_TYPES:
            raise ValueError(f"Unsupported artifact_type: {artifact_type}")

        canonical_key = str(value.get("canonical_key", "")).strip()
        title = str(value.get("title", "")).strip()
        if not canonical_key or not title:
            raise ValueError("canonical_key and title are required")

        evidence = value.get("evidence", [])
        if not isinstance(evidence, list):
            raise ValueError("evidence must be an array")

        return cls(
            artifact_type=artifact_type,
            canonical_key=canonical_key,
            title=title,
            date=str(value.get("date", "")),
            fields=dict(value.get("fields", {})),
            signals=dict(value.get("signals", {})),
            evidence=[SourceEvidence.from_dict(item) for item in evidence],
            warnings=[str(item) for item in value.get("warnings", [])],
        )
