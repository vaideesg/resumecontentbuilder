from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when candidate configuration is invalid."""


def load_candidate_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"Candidate config not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Candidate config is not valid JSON: {exc}") from exc

    if config.get("schema_version") != "1.0":
        raise ConfigError("candidate.config.json must use schema_version '1.0'")

    candidate = config.get("candidate")
    if not isinstance(candidate, dict):
        raise ConfigError("candidate must be an object")

    canonical_name = candidate.get("canonical_name")
    if not isinstance(canonical_name, str) or not canonical_name.strip():
        raise ConfigError("candidate.canonical_name is required")

    for field in ("known_name_variants", "employment", "professional_profiles", "known_collaborators"):
        value = candidate.get(field, [])
        if not isinstance(value, list):
            raise ConfigError(f"candidate.{field} must be an array")

    return config
