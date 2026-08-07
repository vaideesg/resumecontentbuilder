from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from artifact_finder import run_pipeline  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Render verified professional artifact records.")
    parser.add_argument("--candidate-config", required=True)
    parser.add_argument("--records", required=True, help="Normalized JSONL records from discovery agents.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--portfolio-dir",
        help="Directory for the consolidated candidate Markdown file. Defaults to --output-dir.",
    )
    parser.add_argument(
        "--portfolio-file",
        help="Markdown filename for the portfolio. Defaults to a slug of the canonical name.",
    )
    parser.add_argument("--consent-confirmed", action="store_true")
    parser.add_argument("--include-possible", action="store_true")
    args = parser.parse_args()

    try:
        manifest = run_pipeline(
            args.candidate_config,
            args.records,
            args.output_dir,
            consent_confirmed=args.consent_confirmed,
            include_possible=args.include_possible,
            portfolio_dir=args.portfolio_dir,
            portfolio_file=args.portfolio_file,
        )
    except (OSError, ValueError) as exc:
        print(f"artifact-finder: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
