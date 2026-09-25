from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DirectTopology:
    schema: str
    principal: str
    formation: str = "direct-single-process"

    @classmethod
    def direct(cls, principal: str) -> "DirectTopology":
        return cls(
            schema="harness-rig/execution-plan/experimental-direct-v1",
            principal=principal,
        )
