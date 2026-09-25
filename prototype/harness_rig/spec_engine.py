from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .authority import AuthorityRef


SPEC_ENGINE_SCHEMA = "harness-rig/spec-engine/experimental-v1"


@dataclass(frozen=True)
class SpecEngineHealth:
    """Experimental provider-neutral readiness summary.

    This is deliberately not a Stable core contract. It contains only the
    observations needed by the current M6 consumers and can still change when a
    second SpecEngine is implemented.
    """

    schema: str
    engine: str
    version: str | None
    change: str
    root_identity: str | None
    schema_name: str | None
    planning_complete: bool
    tasks_complete: bool
    outcome: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class SpecArchiveMutation:
    engine: str
    change: str
    outcome: str
    reasons: tuple[str, ...]
    archived_path: str | None
    specs_updated: bool | None


class SpecEngine(Protocol):
    """Minimum Experimental interface earned by the M6 archive consumer."""

    def available(self) -> bool: ...

    def health(self, change: str, *, require_tasks_complete: bool = False) -> SpecEngineHealth: ...

    def authority_ref(self, change: str, *, subject_ref: str) -> AuthorityRef: ...

    def archive(self, change: str) -> SpecArchiveMutation: ...
