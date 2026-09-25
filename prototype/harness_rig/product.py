from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

from .canonical import digest

CLI_ENVELOPE_SCHEMA = "harness-rig/cli-envelope/v1"
CONFIG_SCHEMA = "harness-rig/config/v1"
PRODUCT_REVISION = "r8.10"

EXIT_PASS = 0
EXIT_BLOCKED = 2
EXIT_FAIL = 3
EXIT_INVALID = 4
EXIT_INTERNAL = 5
EXIT_TIMEOUT = 124
EXIT_CANCELLED = 130

_OUTCOME_EXIT = {
    "PASS": EXIT_PASS,
    "BLOCKED": EXIT_BLOCKED,
    "FAIL": EXIT_FAIL,
    "INVALID": EXIT_INVALID,
    "ERROR": EXIT_INTERNAL,
    "TIMEOUT": EXIT_TIMEOUT,
    "CANCELLED": EXIT_CANCELLED,
}


class ProductError(ValueError):
    pass


@dataclass(frozen=True)
class CliEnvelope:
    schema: str
    command: str
    outcome: str
    exit_code: int
    data: Mapping[str, Any] | None = None
    reasons: tuple[str, ...] = ()
    compatibility: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["reasons"] = list(self.reasons)
        return out

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


def envelope(command: str, outcome: str, *, data: Mapping[str, Any] | None = None,
             reasons: tuple[str, ...] = (), compatibility: str | None = None) -> CliEnvelope:
    if outcome not in _OUTCOME_EXIT:
        raise ProductError(f"unknown-cli-outcome:{outcome}")
    return CliEnvelope(
        schema=CLI_ENVELOPE_SCHEMA,
        command=command,
        outcome=outcome,
        exit_code=_OUTCOME_EXIT[outcome],
        data=data,
        reasons=reasons,
        compatibility=compatibility,
    )


def load_cli_envelope(payload: Mapping[str, Any]) -> CliEnvelope:
    """Strictly load v1, or deterministically wrap the two r8.9 JSON shapes."""
    if payload.get("schema") == CLI_ENVELOPE_SCHEMA:
        allowed = {"schema", "command", "outcome", "exit_code", "data", "reasons", "compatibility"}
        unknown = set(payload) - allowed
        if unknown:
            raise ProductError(f"cli-envelope-unknown-fields:{sorted(unknown)!r}")
        command = payload.get("command")
        outcome = payload.get("outcome")
        exit_code = payload.get("exit_code")
        reasons = payload.get("reasons", [])
        data = payload.get("data")
        compatibility = payload.get("compatibility")
        if not isinstance(command, str) or not command:
            raise ProductError("cli-envelope-invalid-command")
        if outcome not in _OUTCOME_EXIT or exit_code != _OUTCOME_EXIT[outcome]:
            raise ProductError("cli-envelope-invalid-outcome-exit")
        if not isinstance(reasons, list) or not all(isinstance(x, str) for x in reasons):
            raise ProductError("cli-envelope-invalid-reasons")
        if data is not None and not isinstance(data, dict):
            raise ProductError("cli-envelope-invalid-data")
        if compatibility is not None and not isinstance(compatibility, str):
            raise ProductError("cli-envelope-invalid-compatibility")
        return CliEnvelope(CLI_ENVELOPE_SCHEMA, command, outcome, exit_code, data, tuple(reasons), compatibility)

    # r8.9 direct trust-path JSON compatibility fixture.
    if set(payload) == {"receipt", "verdict"} and isinstance(payload.get("verdict"), dict):
        accepted = payload["verdict"].get("outcome") == "ACCEPTED"
        return envelope(
            "verify", "PASS" if accepted else "BLOCKED",
            data=dict(payload), compatibility="r8.9/direct-json",
        )

    # r8.9 guarded archive JSON compatibility fixture.
    archive_keys = {
        "outcome", "reasons", "authority_before", "state_before", "pre_receipt", "pre_verdict",
        "mutation", "authority_after", "state_after", "transition_receipt", "post_recheck_verdict",
    }
    if archive_keys.issubset(payload):
        old_outcome = payload.get("outcome")
        new_outcome = "PASS" if old_outcome == "PASS" else "BLOCKED"
        reasons = payload.get("reasons", [])
        return envelope(
            "spec archive", new_outcome, data=dict(payload),
            reasons=tuple(str(x) for x in reasons) if isinstance(reasons, list) else (),
            compatibility="r8.9/spec-archive-json",
        )
    raise ProductError("unsupported-cli-envelope-version")


@dataclass(frozen=True)
class ProductConfig:
    schema: str = CONFIG_SCHEMA
    noninteractive: bool = True
    timeout_seconds: float = 30.0
    openspec_executable: str = "openspec"
    sources: tuple[str, ...] = field(default_factory=lambda: ("defaults",))


_ALLOWED_CONFIG = {"schema", "noninteractive", "timeout_seconds", "openspec_executable"}


def _read_config(path: Path, *, tier: str) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductError(f"{tier}-config-malformed:{exc.__class__.__name__}") from exc
    if not isinstance(raw, dict):
        raise ProductError(f"{tier}-config-not-object")
    if tier == "global" and "policy" in raw:
        raise ProductError("global-policy-override-forbidden")
    unknown = set(raw) - _ALLOWED_CONFIG
    if unknown:
        if tier == "global" and "policy" in unknown:
            raise ProductError("global-policy-override-forbidden")
        raise ProductError(f"{tier}-config-unknown-fields:{sorted(unknown)!r}")
    schema = raw.get("schema", CONFIG_SCHEMA)
    if schema != CONFIG_SCHEMA:
        raise ProductError(f"{tier}-config-unsupported-schema:{schema}")
    if "noninteractive" in raw and not isinstance(raw["noninteractive"], bool):
        raise ProductError(f"{tier}-config-invalid-noninteractive")
    if "timeout_seconds" in raw:
        value = raw["timeout_seconds"]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not (0.05 <= float(value) <= 3600):
            raise ProductError(f"{tier}-config-invalid-timeout")
    if "openspec_executable" in raw and (not isinstance(raw["openspec_executable"], str) or not raw["openspec_executable"]):
        raise ProductError(f"{tier}-config-invalid-openspec-executable")
    return raw


def global_config_path(env: Mapping[str, str] | None = None, home: Path | None = None) -> Path:
    e = os.environ if env is None else env
    if e.get("HARNESS_RIG_GLOBAL_CONFIG"):
        return Path(e["HARNESS_RIG_GLOBAL_CONFIG"]).expanduser()
    if e.get("XDG_CONFIG_HOME"):
        return Path(e["XDG_CONFIG_HOME"]) / "harness-rig" / "config.json"
    base = Path.home() if home is None else home
    return base / ".config" / "harness-rig" / "config.json"


def project_config_path(repo: Path) -> Path:
    return repo.resolve() / ".harness-rig" / "config.json"


def load_effective_config(repo: Path, *, cli: Mapping[str, Any] | None = None,
                          env: Mapping[str, str] | None = None, home: Path | None = None) -> ProductConfig:
    values: dict[str, Any] = {
        "noninteractive": True,
        "timeout_seconds": 30.0,
        "openspec_executable": "openspec",
    }
    sources = ["defaults"]
    gp = global_config_path(env, home)
    global_raw = _read_config(gp, tier="global")
    if global_raw:
        values.update({k: v for k, v in global_raw.items() if k != "schema"})
        sources.append(f"global:{gp}")
    pp = project_config_path(repo)
    project_raw = _read_config(pp, tier="project")
    if project_raw:
        values.update({k: v for k, v in project_raw.items() if k != "schema"})
        sources.append(f"project:{pp}")
    if cli:
        overrides = {k: v for k, v in cli.items() if v is not None}
        unknown = set(overrides) - {"noninteractive", "timeout_seconds", "openspec_executable"}
        if unknown:
            raise ProductError(f"cli-config-unknown-fields:{sorted(unknown)!r}")
        if overrides:
            values.update(overrides)
            sources.append("cli")
    # Reuse the same validation by materializing an in-memory shape.
    if not isinstance(values["noninteractive"], bool):
        raise ProductError("effective-config-invalid-noninteractive")
    timeout = values["timeout_seconds"]
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not (0.05 <= float(timeout) <= 3600):
        raise ProductError("effective-config-invalid-timeout")
    executable = values["openspec_executable"]
    if not isinstance(executable, str) or not executable:
        raise ProductError("effective-config-invalid-openspec-executable")
    return ProductConfig(
        noninteractive=values["noninteractive"],
        timeout_seconds=float(timeout),
        openspec_executable=executable,
        sources=tuple(sources),
    )


def config_fingerprint(config: ProductConfig) -> str:
    return digest({
        "schema": config.schema,
        "noninteractive": config.noninteractive,
        "timeout_seconds": config.timeout_seconds,
        "openspec_executable": config.openspec_executable,
    })
