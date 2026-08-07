from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .models import ArtifactRecord


SECTION_ORDER = [
    ("patents", "Patents"),
    ("standards-publications", "Standards Publications"),
    ("white-papers", "White Papers"),
    ("articles", "Articles"),
    ("tech-talks", "Technical Talks"),
    ("certifications", "Certifications"),
    ("community-contributions", "Open Source and Community Contributions"),
]


def candidate_markdown_filename(canonical_name: str) -> str:
    normalized = "".join(
        character.lower() if character.isascii() and character.isalnum() else "-"
        for character in canonical_name.strip()
    )
    slug = "-".join(part for part in normalized.split("-") if part)
    return f"{slug or 'candidate'}.md"


def render_candidate_markdown(
    path: Path,
    *,
    candidate: dict[str, Any],
    included_records: list[ArtifactRecord],
    generated_at: str,
    run_status: str,
) -> None:
    grouped: dict[str, list[ArtifactRecord]] = defaultdict(list)
    for record in included_records:
        grouped[record.artifact_type].append(record)

    canonical_name = str(candidate["canonical_name"])
    is_demo = any(bool(record.fields.get("demo_only")) for record in included_records)
    lines = [
        f"# {canonical_name}",
        "",
        "> Evidence-backed professional artifact portfolio generated from public sources.",
    ]
    if is_demo:
        lines.extend(
            [
                "",
                "> **Demonstration only:** Artifact entries marked `[DEMO]` are synthetic examples "
                "showing output structure. They are not factual claims about the candidate.",
            ]
        )
    lines.extend(
        [
            "",
            "## Portfolio Summary",
            "",
            f"- **Verified artifacts:** {len(included_records)}",
        ]
    )

    employment = candidate.get("employment", [])
    if employment:
        companies = sorted(
            {
                str(item.get("company", "")).strip()
                for item in employment
                if str(item.get("company", "")).strip()
            }
        )
        if companies:
            lines.append(f"- **Known professional affiliations:** {', '.join(companies)}")

    lines.extend(["", "## Artifact Counts", ""])
    for artifact_type, heading in SECTION_ORDER:
        count = len(grouped.get(artifact_type, []))
        if count:
            lines.append(f"- **{heading}:** {count}")

    for artifact_type, heading in SECTION_ORDER:
        records = sorted(
            grouped.get(artifact_type, []),
            key=lambda item: (item.date, item.title.casefold(), item.canonical_key),
            reverse=True,
        )
        if not records:
            continue
        lines.extend(["", f"## {heading}", ""])
        lines.extend(_record_lines(artifact_type, record) for record in records)
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _record_lines(artifact_type: str, record: ArtifactRecord) -> str:
    fields = record.fields
    date = _first(
        fields,
        "published_date",
        "filing_date",
        "delivery_date",
        "issue_date",
        "start_date",
    ) or record.date
    url = _first(
        fields,
        "canonical_url",
        "url",
        "verification_url",
        "recording_url",
    )
    title = f"[{record.title}]({url})" if url else record.title
    details: list[str] = []

    if date:
        details.append(date)
    detail_keys = {
        "patents": ("type", "patent_number", "current_status"),
        "standards-publications": ("type", "identifier", "role", "status"),
        "white-papers": ("type", "domain", "website"),
        "articles": ("type", "category", "website", "impressions"),
        "tech-talks": ("type", "event", "where", "speaker_role"),
        "certifications": ("type", "issuer", "status"),
        "community-contributions": ("type", "project", "role"),
    }[artifact_type]
    for key in detail_keys:
        value = fields.get(key)
        if value not in (None, "", []):
            label = key.replace("_", " ").title()
            details.append(f"{label}: {_format(value)}")

    suffix = f" — {'; '.join(details)}" if details else ""
    return f"- **{title}**{suffix}"


def _first(fields: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = fields.get(key)
        if value not in (None, "", []):
            return _format(value)
    return ""


def _format(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(sorted(str(item) for item in value))
    return str(value)
