from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from artifact_finder.confidence import score_identity
from artifact_finder.config import ConfigError, load_candidate_config
from artifact_finder.models import ArtifactRecord
from artifact_finder.pipeline import run_pipeline
from artifact_finder.reconcile import reconcile_records
from artifact_finder.render import ENRICHED_SCHEMAS


class ConfigTests(unittest.TestCase):
    def test_loads_shared_candidate_config(self) -> None:
        config = load_candidate_config(PLUGIN_ROOT / "candidate.config.json")
        self.assertTrue(config["candidate"]["canonical_name"])

    def test_rejects_missing_candidate_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.json"
            path.write_text('{"schema_version":"1.0","candidate":{}}', encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_candidate_config(path)


class ConfidenceTests(unittest.TestCase):
    def test_name_alone_is_not_confirmed(self) -> None:
        result = score_identity({"name": 1.0})
        self.assertEqual("possible", result.label)

    def test_multiple_corrobators_confirm_identity(self) -> None:
        result = score_identity(
            {
                "name": 1.0,
                "affiliation": 1.0,
                "collaborators": 1.0,
                "topic": 0.9,
                "timeline": 1.0,
            }
        )
        self.assertEqual("confirmed", result.label)

    def test_rejects_non_finite_signal(self) -> None:
        with self.assertRaises(ValueError):
            score_identity({"name": float("nan")})


class ReconciliationTests(unittest.TestCase):
    def test_grant_supersedes_application_for_same_filing(self) -> None:
        application = ArtifactRecord.from_dict(
            {
                "artifact_type": "patents",
                "canonical_key": "US|app|1",
                "title": "Example",
                "fields": {"type": "Application"},
            }
        )
        grant = ArtifactRecord.from_dict(
            {
                "artifact_type": "patents",
                "canonical_key": "US|app|1",
                "title": "Example",
                "fields": {"type": "Grant"},
            }
        )
        result = reconcile_records([application, grant])
        self.assertEqual(1, len(result))
        self.assertEqual("Grant", result[0].fields["type"])

    def test_distinct_continuations_remain_separate(self) -> None:
        first = ArtifactRecord.from_dict(
            {
                "artifact_type": "patents",
                "canonical_key": "US|app|1",
                "title": "Example",
            }
        )
        second = ArtifactRecord.from_dict(
            {
                "artifact_type": "patents",
                "canonical_key": "US|app|2",
                "title": "Example",
            }
        )
        self.assertEqual(2, len(reconcile_records([first, second])))

    def test_tied_records_are_order_independent(self) -> None:
        first = ArtifactRecord.from_dict(
            {
                "artifact_type": "articles",
                "canonical_key": "article|1",
                "title": "Example",
                "fields": {"website": "Alpha"},
            }
        )
        second = ArtifactRecord.from_dict(
            {
                "artifact_type": "articles",
                "canonical_key": "article|1",
                "title": "Example",
                "fields": {"website": "Beta"},
            }
        )
        forward = reconcile_records([first, second])[0].fields["website"]
        reverse = reconcile_records([second, first])[0].fields["website"]
        self.assertEqual(forward, reverse)


class PipelineTests(unittest.TestCase):
    def test_pipeline_writes_compatibility_and_audit_outputs(self) -> None:
        record = {
            "artifact_type": "patents",
            "canonical_key": "US|app|1",
            "title": "Example patent",
            "date": "2022-01-15",
            "fields": {
                "patent_number": "12345678",
                "application_number": "20240001234",
                "type": "Grant",
                "filed": "January 15, 2022",
                "inventors": "Candidate Name",
            },
            "signals": {
                "name": 1.0,
                "affiliation": 1.0,
                "collaborators": 1.0,
                "topic": 0.9,
                "timeline": 1.0,
            },
            "evidence": [
                {
                    "evidence_id": "ev-1",
                    "source_url": "https://example.test/patent",
                    "retrieved_at": "2026-08-07T00:00:00Z",
                    "authority_rank": 1,
                    "field": "status",
                    "raw_value": "Grant",
                    "normalized_value": "Grant",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            records = root / "records.jsonl"
            records.write_text(json.dumps(record) + "\n", encoding="utf-8")
            output = root / "out"
            manifest = run_pipeline(
                PLUGIN_ROOT / "candidate.config.json",
                records,
                output,
                consent_confirmed=True,
                portfolio_dir=root,
            )

            self.assertEqual(1, manifest["included_records"])
            self.assertTrue((output / "patents.csv").exists())
            self.assertTrue((output / "identity-decisions.jsonl").exists())
            self.assertTrue((output / "dedup-decisions.jsonl").exists())
            self.assertTrue((output / "status-events.jsonl").exists())
            self.assertTrue((output / "conflicts.jsonl").exists())
            self.assertTrue((output / "query-plan.json").exists())
            self.assertTrue((output / "run-report.json").exists())
            self.assertTrue((output / "source-snapshots").is_dir())
            portfolio = Path(manifest["portfolio_file"])
            self.assertTrue(portfolio.exists())
            portfolio_text = portfolio.read_text(encoding="utf-8")
            candidate = load_candidate_config(PLUGIN_ROOT / "candidate.config.json")["candidate"]
            self.assertIn(f"# {candidate['canonical_name']}", portfolio_text)
            self.assertEqual("vaideeswaran-ganesan.md", portfolio.name)
            self.assertIn("## Patents", portfolio_text)
            self.assertIn("Example patent", portfolio_text)
            self.assertNotIn("Run status", portfolio_text)
            self.assertNotIn("Evidence snapshot", portfolio_text)
            self.assertNotIn("## Methodology", portfolio_text)
            self.assertNotIn("## Articles", portfolio_text)
            with (output / "patents.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual("12345678", rows[0]["Patent Number"])
            with (output / "patents.enriched.csv").open(encoding="utf-8", newline="") as handle:
                enriched_reader = csv.DictReader(handle)
                self.assertEqual(ENRICHED_SCHEMAS["patents"], enriched_reader.fieldnames)

    def test_pipeline_requires_consent(self) -> None:
        with self.assertRaises(ValueError):
            run_pipeline("missing.json", "missing.jsonl", "out", consent_confirmed=False)

    def test_malformed_evidence_has_contextual_error(self) -> None:
        record = {
            "artifact_type": "articles",
            "canonical_key": "article|1",
            "title": "Example",
            "evidence": ["bad"],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            records = root / "records.jsonl"
            records.write_text(json.dumps(record) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Each evidence entry must be an object"):
                run_pipeline(
                    PLUGIN_ROOT / "candidate.config.json",
                    records,
                    root / "out",
                    consent_confirmed=True,
                )


if __name__ == "__main__":
    unittest.main()
