"""M5 Context knowledge lifecycle semantics.

This module owns deterministic, module-local rules for stable knowledge identity,
external-source freshness comparison, and source-claim reconciliation. It does
not own host projection or introduce a retrieval/index service.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


FRESH = "FRESH"
STALE = "STALE"
UNKNOWN = "UNKNOWN"
SUPPORTED = "SUPPORTED"
CONFLICT = "CONFLICT"
UNSUPPORTED = "UNSUPPORTED"


class StableIdError(ValueError):
    """Raised when a canonical knowledge ID lifecycle rule is violated."""


class StableIdRegistry:
    """Small in-memory model of the canonical stable-ID lifecycle.

    The registry is deliberately not a persistence service. Canonical pages and
    optional lineage metadata remain the durable source of truth.
    """

    def __init__(self, active: dict[str, str] | None = None, retired: Iterable[str] = ()) -> None:
        self._active = dict(active or {})
        self._retired = set(retired)
        overlap = set(self._active).intersection(self._retired)
        if overlap:
            raise StableIdError(f"active-and-retired:{sorted(overlap)!r}")

    @property
    def active(self) -> dict[str, str]:
        return dict(self._active)

    @property
    def retired(self) -> frozenset[str]:
        return frozenset(self._retired)

    def register(self, stable_id: str, path: str) -> None:
        self._ensure_new(stable_id)
        self._active[stable_id] = path

    def rename_or_move(self, stable_id: str, new_path: str) -> None:
        self._require_active(stable_id)
        self._active[stable_id] = new_path

    def split(self, stable_id: str, *, primary_path: str, additional: dict[str, str]) -> None:
        """Keep the original ID on the primary successor; new topics get new IDs."""
        self._require_active(stable_id)
        for new_id in additional:
            self._ensure_new(new_id)
        self._active[stable_id] = primary_path
        self._active.update(additional)

    def merge(self, survivor_id: str, absorbed_ids: Iterable[str], *, survivor_path: str | None = None) -> None:
        """Keep one active ID and permanently retire absorbed IDs."""
        self._require_active(survivor_id)
        absorbed = tuple(absorbed_ids)
        if survivor_id in absorbed:
            raise StableIdError("merge-survivor-cannot-be-absorbed")
        for stable_id in absorbed:
            self._require_active(stable_id)
        if survivor_path is not None:
            self._active[survivor_id] = survivor_path
        for stable_id in absorbed:
            del self._active[stable_id]
            self._retired.add(stable_id)

    def retire(self, stable_id: str) -> None:
        self._require_active(stable_id)
        del self._active[stable_id]
        self._retired.add(stable_id)

    def _require_active(self, stable_id: str) -> None:
        if stable_id not in self._active:
            raise StableIdError(f"unknown-active-id:{stable_id}")

    def _ensure_new(self, stable_id: str) -> None:
        if stable_id in self._active:
            raise StableIdError(f"duplicate-active-id:{stable_id}")
        if stable_id in self._retired:
            raise StableIdError(f"retired-id-reuse:{stable_id}")


@dataclass(frozen=True)
class SourceObservation:
    """Recorded/observed identity for one external source.

    ``page_updated`` is intentionally absent: canonical page edit time is not
    external-source freshness evidence.
    """

    source: str
    checked_date: str
    version: str | None = None
    commit: str | None = None


def source_freshness(recorded: SourceObservation, observed: SourceObservation) -> str:
    """Compare a recorded source baseline with a newly observed baseline."""
    if recorded.source != observed.source:
        raise ValueError("source-identity-mismatch")
    comparisons: list[bool] = []
    if recorded.version is not None and observed.version is not None:
        comparisons.append(recorded.version == observed.version)
    if recorded.commit is not None and observed.commit is not None:
        comparisons.append(recorded.commit == observed.commit)
    if not comparisons:
        return UNKNOWN
    return FRESH if all(comparisons) else STALE


@dataclass(frozen=True)
class SourceClaim:
    source: str
    claim_id: str
    value: str | None
    note: str = ""


@dataclass(frozen=True)
class ReconciliationResult:
    claim_id: str
    proposed_value: str
    status: str
    supported_value: str | None
    sources: tuple[str, ...]
    conflicting_values: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()

    @property
    def publishable(self) -> bool:
        return self.status == SUPPORTED


def reconcile_claim(
    claim_id: str,
    proposed_value: str,
    observations: Iterable[SourceClaim],
) -> ReconciliationResult:
    """Preserve conflicts/gaps and only accept a directly supported conclusion."""
    relevant = tuple(o for o in observations if o.claim_id == claim_id)
    values = sorted({o.value for o in relevant if o.value is not None})
    gaps = tuple(sorted(o.source for o in relevant if o.value is None))
    sources = tuple(sorted({o.source for o in relevant}))

    if len(values) > 1:
        return ReconciliationResult(
            claim_id=claim_id,
            proposed_value=proposed_value,
            status=CONFLICT,
            supported_value=None,
            sources=sources,
            conflicting_values=tuple(values),
            gaps=gaps,
        )
    if not values or values[0] != proposed_value:
        return ReconciliationResult(
            claim_id=claim_id,
            proposed_value=proposed_value,
            status=UNSUPPORTED,
            supported_value=values[0] if values else None,
            sources=sources,
            gaps=gaps,
        )
    return ReconciliationResult(
        claim_id=claim_id,
        proposed_value=proposed_value,
        status=SUPPORTED,
        supported_value=values[0],
        sources=sources,
        gaps=gaps,
    )
