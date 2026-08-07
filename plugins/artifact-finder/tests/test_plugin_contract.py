from __future__ import annotations

import json
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SKILLS = {
    "artifact-finder",
    "collect-artifacts",
    "patent-finder",
    "whitepaper-finder",
    "article-finder",
    "tech-talk-finder",
    "certification-finder",
    "standards-publication-finder",
    "community-contribution-finder",
}


class PluginContractTests(unittest.TestCase):
    def test_manifest_and_all_skill_entries_exist(self) -> None:
        manifest_path = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual("artifact-finder", manifest["name"])

        actual = {
            path.parent.name
            for path in (PLUGIN_ROOT / "skills").glob("*/SKILL.md")
        }
        self.assertEqual(EXPECTED_SKILLS, actual)

    def test_skill_frontmatter_matches_directory(self) -> None:
        for skill_name in EXPECTED_SKILLS:
            content = (PLUGIN_ROOT / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\n"), skill_name)
            self.assertIn(f"\nname: {skill_name}\n", content, skill_name)
            self.assertTrue(
                "candidate_config" in content or "candidate.config.json" in content,
                skill_name,
            )
            self.assertIn("consent", content.casefold(), skill_name)

    def test_candidate_details_exist_only_in_config(self) -> None:
        config = json.loads((PLUGIN_ROOT / "candidate.config.json").read_text(encoding="utf-8"))
        candidate = config["candidate"]
        forbidden = {
            candidate["canonical_name"],
            *candidate.get("known_name_variants", []),
            *(item["company"] for item in candidate.get("employment", [])),
            *(item["url"] for item in candidate.get("professional_profiles", [])),
        }

        reusable_roots = [PLUGIN_ROOT / "skills", PLUGIN_ROOT / "scripts", PLUGIN_ROOT / "docs"]
        for root in reusable_roots:
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in {".md", ".py", ".json"}:
                    continue
                content = path.read_text(encoding="utf-8")
                for value in forbidden:
                    if len(value) >= 5:
                        self.assertNotIn(value, content, f"{value!r} leaked into {path}")


if __name__ == "__main__":
    unittest.main()
