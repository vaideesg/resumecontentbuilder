from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .confidence import score_identity
from .config import load_candidate_config
from .models import ArtifactRecord
from .reconcile import reconcile_records
from .render import (
    COMPATIBILITY_SCHEMAS,
    ENRICHED_SCHEMAS,
    stable_record_id,
    write_csv,
    write_json,
    write_jsonl,
)


def run_pipeline(
    candidate_config: str | Path,
    records_path: str | Path,
    output_dir: str | Path,
    *,
    consent_confirmed: bool,
    include_possible: bool = False,
) -> dict[str, Any]:
    if not consent_confirmed:
        raise ValueError("consent_confirmed=true is required")

    config = load_candidate_config(candidate_config)
    records = _load_records(Path(records_path))
    reconciled = reconcile_records(records)
    output_path = Path(output_dir)
    retrieved_at = _snapshot_timestamp(reconciled)

    decisions: list[dict[str, Any]] = []
    outputs: dict[str, list[dict[str, Any]]] = {key: [] for key in COMPATIBILITY_SCHEMAS}
    enriched: dict[str, list[dict[str, Any]]] = {key: [] for key in COMPATIBILITY_SCHEMAS}

    for record in reconciled:
        confidence = score_identity(record.signals)
        decision = _decision(confidence.label, include_possible)
        record_id = stable_record_id(record.artifact_type, record.canonical_key)
        evidence_ids = sorted(item.evidence_id for item in record.evidence)
        source_urls = sorted({item.source_url for item in record.evidence if item.source_url})
        record_confidence = _record_confidence(record)
        status_confidence = _status_confidence(record)

        decision_row = {
            "record_id": record_id,
            "artifact_type": record.artifact_type,
            "canonical_key": record.canonical_key,
            "decision": decision,
            "identity_confidence": confidence.score,
            "confidence_label": confidence.label,
            "evidence_coverage": confidence.coverage,
            "record_confidence": record_confidence,
            "status_confidence": status_confidence,
            "confidence_reasons": list(confidence.reasons),
            "evidence_ids": evidence_ids,
            "warnings": record.warnings,
        }
        decisions.append(decision_row)

        enriched_row = _enriched_row(
            record,
            record_id=record_id,
            identity_confidence=confidence.score,
            record_confidence=record_confidence,
            status_confidence=status_confidence,
            evidence_coverage=confidence.coverage,
            decision=decision,
            confidence_reasons=";".join(confidence.reasons),
            source_urls=";".join(source_urls),
            retrieved_at=retrieved_at,
        )
        enriched[record.artifact_type].append(enriched_row)

        if decision == "include":
            outputs[record.artifact_type].append(_compatibility_row(record))

    for artifact_type, headers in COMPATIBILITY_SCHEMAS.items():
        compatibility_rows = sorted(
            outputs[artifact_type],
            key=lambda row: tuple(str(row.get(header, "")).casefold() for header in headers),
        )
        write_csv(output_path / _compatibility_filename(artifact_type), headers, compatibility_rows)

        enriched_rows = sorted(enriched[artifact_type], key=lambda row: row["record_id"])
        write_csv(
            output_path / f"{artifact_type}.enriched.csv",
            ENRICHED_SCHEMAS[artifact_type],
            enriched_rows,
        )

    write_jsonl(output_path / "identity-decisions.jsonl", sorted(decisions, key=lambda row: row["record_id"]))
    write_jsonl(output_path / "dedup-decisions.jsonl", _dedup_decisions(records))
    write_jsonl(output_path / "status-events.jsonl", _status_events(reconciled))
    write_jsonl(output_path / "conflicts.jsonl", _conflicts(reconciled))
    write_json(
        output_path / "query-plan.json",
        {
            "schema_version": "1.0",
            "artifact_types": sorted({record.artifact_type for record in records}),
            "candidate_config": str(Path(candidate_config)),
            "offline": False,
            "input_records": len(records),
        },
    )
    (output_path / "source-snapshots").mkdir(parents=True, exist_ok=True)

    decision_counts = Counter(row["decision"] for row in decisions)
    degraded = bool(decision_counts.get("uncertain")) or any(record.warnings for record in reconciled)
    manifest = {
        "schema_version": "1.0",
        "candidate_config": str(Path(candidate_config)),
        "candidate_name": config["candidate"]["canonical_name"],
        "consent_confirmed": True,
        "include_possible": include_possible,
        "input_records": len(records),
        "reconciled_records": len(reconciled),
        "included_records": sum(len(rows) for rows in outputs.values()),
        "generated_at": retrieved_at,
        "status": "COMPLETE_DEGRADED" if degraded else "COMPLETE",
    }
    write_json(output_path / "run-manifest.json", manifest)
    checksums = _output_checksums(output_path)
    write_json(
        output_path / "run-report.json",
        {
            "schema_version": "1.0",
            "status": manifest["status"],
            "artifact_types": sorted({record.artifact_type for record in records}),
            "decision_counts": dict(sorted(decision_counts.items())),
            "warning_count": sum(len(record.warnings) for record in reconciled),
            "source_count": len(
                {
                    evidence.source_url
                    for record in reconciled
                    for evidence in record.evidence
                    if evidence.source_url
                }
            ),
            "source_independence": _source_independence(reconciled),
            "checksums": checksums,
            "generated_at": retrieved_at,
        },
    )
    return manifest


def _load_records(path: Path) -> list[ArtifactRecord]:
    records: list[ArtifactRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(ArtifactRecord.from_dict(json.loads(line)))
            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                raise ValueError(f"Invalid record at {path}:{line_number}: {exc}") from exc
    return records


def _decision(label: str, include_possible: bool) -> str:
    if label in {"confirmed", "probable"}:
        return "include"
    if label == "possible" and include_possible:
        return "include"
    if label == "possible":
        return "uncertain"
    return "exclude"


def _snapshot_timestamp(records: list[ArtifactRecord]) -> str:
    timestamps = sorted(
        evidence.retrieved_at
        for record in records
        for evidence in record.evidence
        if evidence.retrieved_at
    )
    return timestamps[-1] if timestamps else ""


def _record_confidence(record: ArtifactRecord) -> float:
    if not record.evidence:
        return 0.0
    authority_values = [max(0.0, min(1.0, (6 - evidence.authority_rank) / 5)) for evidence in record.evidence]
    source_count_bonus = min(0.1, len({evidence.source_url for evidence in record.evidence}) * 0.025)
    return round(min(1.0, sum(authority_values) / len(authority_values) + source_count_bonus), 4)


def _status_confidence(record: ArtifactRecord) -> float:
    import math

    explicit = record.fields.get("status_confidence")
    if explicit is not None:
        numeric = float(explicit)
        if not math.isfinite(numeric):
            raise ValueError("status_confidence must be a finite number")
        return round(max(0.0, min(1.0, numeric)), 4)
    if record.artifact_type not in {"patents", "certifications", "standards-publications"}:
        return 0.0
    status_evidence = [
        evidence
        for evidence in record.evidence
        if evidence.field.casefold() in {"status", "type", "current_status"}
    ]
    if not status_evidence:
        return 0.0
    return round(max((6 - evidence.authority_rank) / 5 for evidence in status_evidence), 4)


def _compatibility_filename(artifact_type: str) -> str:
    return {
        "white-papers": "white-papers.csv",
        "tech-talks": "tech-talks.csv",
        "standards-publications": "standards-publications.csv",
        "community-contributions": "community-contributions.csv",
    }.get(artifact_type, f"{artifact_type}.csv")


def _compatibility_row(record: ArtifactRecord) -> dict[str, Any]:
    fields = record.fields
    if record.artifact_type == "patents":
        current_status = str(fields.get("current_status", ""))
        compatibility_type = fields.get("type", "")
        if not compatibility_type:
            compatibility_type = {
                "Granted": "Grant",
                "Grant": "Grant",
                "Abandoned": "Abandoned",
                "Published/Pending": "Application",
                "Published": "Application",
                "Application": "Application",
            }.get(current_status, "")
        return {
            "Title": record.title,
            "Patent Number": fields.get("patent_number", _first_value(fields.get("grant_numbers", ""))),
            "Application Number": fields.get(
                "application_number",
                _first_value(fields.get("publication_numbers", "")),
            ),
            "Type": compatibility_type,
            "Filed": fields.get("filed", fields.get("filing_date", record.date)),
            "Inventors": fields.get("inventors", ""),
        }
    if record.artifact_type == "white-papers":
        return {
            "Title": record.title,
            "Published Date": fields.get("published_date", record.date),
            "Type": fields.get("type", ""),
            "Domain": fields.get("domain", ""),
            "Website": fields.get("website", ""),
        }
    if record.artifact_type == "articles":
        return {
            "Title": record.title,
            "Published Date": fields.get("published_date", record.date),
            "Type": fields.get("type", ""),
            "Category": fields.get("category", ""),
            "Website": fields.get("website", ""),
            "Impressions": fields.get("impressions", ""),
        }
    if record.artifact_type == "tech-talks":
        return {
            "Talk": record.title,
            "Published Date": fields.get("published_date", record.date),
            "Type": fields.get("type", ""),
            "Where": fields.get("where", ""),
        }
    if record.artifact_type == "certifications":
        return {
            "Certification": record.title,
            "Published Date": fields.get("published_date", record.date),
            "Type": fields.get("type", ""),
            "Where": fields.get("where", ""),
        }
    if record.artifact_type == "standards-publications":
        return {
            "Title": record.title,
            "Published Date": fields.get("published_date", record.date),
            "Type": fields.get("type", ""),
            "Standards Body": fields.get("standards_body", ""),
            "Working Group": fields.get("working_group", ""),
            "Role": fields.get("role", ""),
            "Identifier": fields.get("identifier", ""),
            "Status": fields.get("status", ""),
            "URL": fields.get("url", ""),
        }
    return {
        "Contribution": record.title,
        "Date": fields.get("date", record.date),
        "Type": fields.get("type", ""),
        "Project": fields.get("project", ""),
        "Role": fields.get("role", ""),
        "URL": fields.get("url", ""),
    }


def _enriched_row(
    record: ArtifactRecord,
    *,
    record_id: str,
    identity_confidence: float,
    record_confidence: float,
    status_confidence: float,
    evidence_coverage: float,
    decision: str,
    confidence_reasons: str,
    source_urls: str,
    retrieved_at: str,
) -> dict[str, Any]:
    row = {
        "record_id": record_id,
        "canonical_key": record.canonical_key,
        **record.fields,
        "identity_confidence": identity_confidence,
        "record_confidence": record_confidence,
        "status_confidence": status_confidence,
        "evidence_coverage": evidence_coverage,
        "decision": decision,
        "confidence_reasons": confidence_reasons,
        "source_urls": source_urls,
        "retrieved_at": retrieved_at,
    }

    title_field = {
        "certifications": "certification",
        "community-contributions": "contribution",
    }.get(record.artifact_type, "title")
    row.setdefault(title_field, record.title)

    date_field = {
        "patents": "filing_date",
        "white-papers": "published_date",
        "articles": "published_date",
        "tech-talks": "delivery_date",
        "certifications": "issue_date",
        "standards-publications": "published_date",
        "community-contributions": "start_date",
    }[record.artifact_type]
    row.setdefault(date_field, record.date)
    return row


def _first_value(value: Any) -> str:
    if isinstance(value, list):
        return str(value[0]) if value else ""
    text = str(value)
    return text.split(";", 1)[0] if text else ""


def _dedup_decisions(records: list[ArtifactRecord]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[ArtifactRecord]] = defaultdict(list)
    for record in records:
        groups[(record.artifact_type, record.canonical_key)].append(record)

    return [
        {
            "artifact_type": artifact_type,
            "canonical_key": canonical_key,
            "input_count": len(group),
            "decision": "merge" if len(group) > 1 else "retain",
            "reason": "same artifact type and canonical key",
        }
        for (artifact_type, canonical_key), group in sorted(groups.items())
    ]


def _status_events(records: list[ArtifactRecord]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for record in records:
        for evidence in record.evidence:
            if evidence.field.casefold() not in {"status", "type", "current_status"}:
                continue
            events.append(
                {
                    "artifact_type": record.artifact_type,
                    "canonical_key": record.canonical_key,
                    "status": evidence.normalized_value or evidence.raw_value,
                    "source_url": evidence.source_url,
                    "retrieved_at": evidence.retrieved_at,
                    "authority_rank": evidence.authority_rank,
                    "evidence_id": evidence.evidence_id,
                }
            )
    return sorted(
        events,
        key=lambda row: (
            row["artifact_type"],
            row["canonical_key"],
            row["retrieved_at"],
            row["evidence_id"],
        ),
    )


def _conflicts(records: list[ArtifactRecord]) -> list[dict[str, Any]]:
    return [
        {
            "artifact_type": record.artifact_type,
            "canonical_key": record.canonical_key,
            "warning": warning,
        }
        for record in sorted(records, key=lambda item: (item.artifact_type, item.canonical_key))
        for warning in sorted(record.warnings)
    ]


def _source_independence(records: list[ArtifactRecord]) -> bool:
    sources_by_type: dict[str, set[str]] = defaultdict(set)
    for record in records:
        for evidence in record.evidence:
            if evidence.source_url:
                sources_by_type[record.artifact_type].add(evidence.source_url)
    return all(len(sources) >= 2 for sources in sources_by_type.values()) if sources_by_type else False


def _output_checksums(output_path: Path) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for path in sorted(output_path.glob("*")):
        if not path.is_file() or path.name == "run-report.json":
            continue
        checksums[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return checksums
