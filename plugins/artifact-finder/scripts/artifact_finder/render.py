from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


COMPATIBILITY_SCHEMAS = {
    "patents": ["Title", "Patent Number", "Application Number", "Type", "Filed", "Inventors"],
    "white-papers": ["Title", "Published Date", "Type", "Domain", "Website"],
    "articles": ["Title", "Published Date", "Type", "Category", "Website", "Impressions"],
    "tech-talks": ["Talk", "Published Date", "Type", "Where"],
    "certifications": ["Certification", "Published Date", "Type", "Where"],
    "standards-publications": [
        "Title",
        "Published Date",
        "Type",
        "Standards Body",
        "Working Group",
        "Role",
        "Identifier",
        "Status",
        "URL",
    ],
    "community-contributions": ["Contribution", "Date", "Type", "Project", "Role", "URL"],
}

COMMON_ENRICHED_SUFFIX = [
    "identity_confidence",
    "record_confidence",
    "evidence_coverage",
    "decision",
    "confidence_reasons",
    "source_urls",
    "retrieved_at",
]

ENRICHED_SCHEMAS = {
    "patents": [
        "record_id",
        "canonical_key",
        "family_id",
        "jurisdiction",
        "application_number",
        "publication_numbers",
        "grant_numbers",
        "title",
        "filing_date",
        "current_status",
        "status_effective_date",
        "inventors",
        "assignees",
        "continuity_type",
        "parent_application",
        "status_confidence",
        *COMMON_ENRICHED_SUFFIX,
    ],
    "white-papers": [
        "record_id",
        "canonical_key",
        "title",
        "published_date",
        "type",
        "domain",
        "website",
        "publisher",
        "authors",
        "document_id",
        "doi",
        "revision",
        "canonical_url",
        "content_hash",
        *COMMON_ENRICHED_SUFFIX,
    ],
    "articles": [
        "record_id",
        "canonical_key",
        "title",
        "published_date",
        "type",
        "category",
        "website",
        "publisher",
        "author_role",
        "co_authors",
        "doi",
        "canonical_url",
        "archive_url",
        "impressions",
        "views",
        "reactions",
        "comments",
        "reposts",
        "metrics_retrieved_at",
        *COMMON_ENRICHED_SUFFIX,
    ],
    "tech-talks": [
        "record_id",
        "canonical_key",
        "talk_series_id",
        "title",
        "type",
        "delivery_date",
        "publication_date",
        "event",
        "organizer",
        "where",
        "venue_mode",
        "speaker_role",
        "co_speakers",
        "recording_url",
        "slides_url",
        "duration_minutes",
        *COMMON_ENRICHED_SUFFIX,
    ],
    "certifications": [
        "record_id",
        "canonical_key",
        "certification",
        "type",
        "issuer",
        "where",
        "level",
        "issue_date",
        "expiration_date",
        "renewal_date",
        "status",
        "public_credential_id",
        "verification_url",
        "status_confidence",
        *COMMON_ENRICHED_SUFFIX,
    ],
    "standards-publications": [
        "record_id",
        "canonical_key",
        "lineage_id",
        "title",
        "published_date",
        "type",
        "standards_body",
        "working_group",
        "committee",
        "role",
        "identifier",
        "status",
        "version",
        "authors_editors",
        "canonical_url",
        "predecessor_ids",
        "successor_ids",
        "updates_ids",
        "updated_by_ids",
        "obsoletes_ids",
        "obsoleted_by_ids",
        "status_history",
        "status_confidence",
        *COMMON_ENRICHED_SUFFIX,
    ],
    "community-contributions": [
        "record_id",
        "canonical_key",
        "contribution",
        "type",
        "project",
        "organization",
        "role",
        "forge",
        "account",
        "repository",
        "contribution_id",
        "start_date",
        "end_date",
        "status",
        "technologies",
        "license",
        "url",
        "package_urls",
        "stars",
        "forks",
        "downloads",
        "contributors",
        "metrics_retrieved_at",
        "questions_posted",
        "answers_posted",
        "accepted_answers",
        "comments_or_replies",
        "reputation_or_points",
        "rank",
        "badges",
        "labels",
        "topic_tags",
        *COMMON_ENRICHED_SUFFIX,
    ],
}


def stable_record_id(artifact_type: str, canonical_key: str) -> str:
    digest = hashlib.sha256(f"v1|{artifact_type}|{canonical_key}".encode("utf-8")).hexdigest()
    return f"rec-{digest[:16]}"


def write_csv(path: Path, headers: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({header: _format_value(row.get(header, "")) for header in headers})


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ";".join(sorted(str(item) for item in value))
    return str(value)
