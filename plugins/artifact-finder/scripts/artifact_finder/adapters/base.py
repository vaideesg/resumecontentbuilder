from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AdapterResult:
    source_name: str
    retrieval_status: str
    assertions: tuple[dict[str, Any], ...] = ()
    warnings: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


class SourceAdapter(ABC):
    """Contract for optional deterministic source adapters."""

    name: str

    @abstractmethod
    def discover(self, query: dict[str, Any]) -> AdapterResult:
        """Return public evidence assertions without making identity decisions."""
