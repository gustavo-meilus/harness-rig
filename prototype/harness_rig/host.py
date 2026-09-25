"""M8 host capability qualification and bounded local-process adapter.

CapabilitySet and RuntimeResolution remain Experimental/module-owned. The first
Stable host candidate is deliberately small: Harness Rig's direct local process
boundary. Stable means only the capabilities explicitly native-qualified here;
unsupported worker/isolation properties fail closed instead of being inferred.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Iterable

from .canonical import digest


CAPABILITY_SCHEMA = "harness-rig/capability-set/experimental-v1"
RESOLUTION_SCHEMA = "harness-rig/runtime-resolution/experimental-v1"
QUALIFICATION_SCHEMA = "harness-rig/host-qualification/v1"
HOST_ID = "local-subprocess"
HOST_ADAPTER_VERSION = "1"

_MATURITY = {"UNSUPPORTED": 0, "IMPLEMENTED": 1, "LOCAL_VERIFIED": 2, "NATIVE_QUALIFIED": 3, "STABLE": 4}


class HostError(ValueError):
    pass


@dataclass(frozen=True)
class CapabilityClaim:
    capability: str
    maturity: str
    supported: bool
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.maturity not in _MATURITY:
            raise HostError(f"invalid-capability-maturity:{self.maturity}")
        if not self.capability:
            raise HostError("empty-capability")
        if self.maturity == "UNSUPPORTED" and self.supported:
            raise HostError("unsupported-capability-cannot-be-supported")
        if self.maturity != "UNSUPPORTED" and not self.supported:
            raise HostError("qualified-capability-must-be-supported")
        if self.maturity == "STABLE" and not self.evidence:
            raise HostError("stable-capability-requires-evidence")
        if self.capability == "isolated_writer" and self.maturity == "STABLE":
            if not any(item.startswith("formal-native:") for item in self.evidence):
                raise HostError("isolated-writer-stable-requires-formal-native-evidence")


@dataclass(frozen=True)
class CapabilitySet:
    schema: str
    host_id: str
    adapter_maturity: str
    claims: tuple[CapabilityClaim, ...]

    def claim(self, capability: str) -> CapabilityClaim:
        for item in self.claims:
            if item.capability == capability:
                return item
        return CapabilityClaim(capability, "UNSUPPORTED", False, ())

    def supports(self, capability: str, *, minimum: str = "STABLE") -> bool:
        claim = self.claim(capability)
        return claim.supported and _MATURITY[claim.maturity] >= _MATURITY[minimum]


@dataclass(frozen=True)
class RuntimeFact:
    key: str
    requested: str | None
    resolved: str | None
    observed: str | None
    status: str


@dataclass(frozen=True)
class RuntimeResolution:
    schema: str
    host_id: str
    adapter_version: str
    launch_id: str
    outcome: str
    facts: tuple[RuntimeFact, ...]
    required_capabilities: tuple[str, ...]
    exit_code: int | None
    stdout_digest: str | None
    stderr_digest: str | None
    reason: str | None


@dataclass(frozen=True)
class HostQualification:
    schema: str
    host_id: str
    adapter_version: str
    adapter_maturity: str
    outcome: str
    capabilities: CapabilitySet
    clean_process: RuntimeResolution
    reasons: tuple[str, ...]
    qualification_id: str


@dataclass(frozen=True)
class FreshVerifierBoundary:
    implementer_id: str
    verifier_id: str
    implementer_context_id: str
    verifier_context_id: str
    verifier_owned_batch: bool
    read_only_required: bool
    read_only_enforced: bool


@dataclass(frozen=True)
class FreshVerifierEligibility:
    outcome: str
    reasons: tuple[str, ...]


def evaluate_fresh_verifier(boundary: FreshVerifierBoundary) -> FreshVerifierEligibility:
    reasons: list[str] = []
    if not boundary.implementer_id or not boundary.verifier_id:
        reasons.append("missing-worker-identity")
    if boundary.implementer_id == boundary.verifier_id:
        reasons.append("verifier-is-implementer")
    if not boundary.implementer_context_id or not boundary.verifier_context_id:
        reasons.append("missing-context-identity")
    elif boundary.implementer_context_id == boundary.verifier_context_id:
        reasons.append("shared-context")
    if boundary.verifier_owned_batch:
        reasons.append("verifier-owned-batch")
    if boundary.read_only_required and not boundary.read_only_enforced:
        reasons.append("read-only-not-enforced")
    return FreshVerifierEligibility("ELIGIBLE" if not reasons else "BLOCKED", tuple(reasons))


def _sha256_bytes(data: bytes) -> str:
    import hashlib
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _facts(*items: RuntimeFact) -> tuple[RuntimeFact, ...]:
    return tuple(items)


def local_capability_set() -> CapabilitySet:
    stable_evidence = ("m8-clean-process-native-probe", "m8-subprocess-boundary-tests")
    unsupported = (
        "fresh_verifier",
        "isolated_worker",
        "read_only_worker",
        "worktree_worker",
        "permission_enforcement",
        "isolated_writer",
    )
    claims = [
        CapabilityClaim("clean_process", "STABLE", True, stable_evidence),
        CapabilityClaim("process_launch", "STABLE", True, stable_evidence),
        CapabilityClaim("runtime_identity_observation", "STABLE", True, stable_evidence),
        CapabilityClaim("crash_reconciliation", "STABLE", True, ("m8-crash-reconciliation-test",)),
    ]
    claims.extend(CapabilityClaim(name, "UNSUPPORTED", False, ()) for name in unsupported)
    return CapabilitySet(CAPABILITY_SCHEMA, HOST_ID, "STABLE", tuple(sorted(claims, key=lambda x: x.capability)))


class LocalProcessHost:
    host_id = HOST_ID
    adapter_version = HOST_ADAPTER_VERSION
    adapter_maturity = "STABLE"

    def capabilities(self) -> CapabilitySet:
        return local_capability_set()

    def launch(
        self,
        argv: Iterable[str],
        *,
        cwd: Path,
        required_capabilities: Iterable[str] = (),
        timeout_seconds: float = 10.0,
        environment: dict[str, str] | None = None,
    ) -> RuntimeResolution:
        args = tuple(str(x) for x in argv)
        required = tuple(sorted(set(str(x) for x in required_capabilities)))
        if not args or not args[0]:
            raise HostError("empty-argv")
        cwd = Path(cwd).resolve()
        if not cwd.is_dir():
            raise HostError("cwd-not-directory")
        caps = self.capabilities()
        missing = tuple(cap for cap in required if not caps.supports(cap))
        requested_exe = args[0]
        resolved_exe = str(Path(requested_exe).resolve()) if os.path.isabs(requested_exe) and Path(requested_exe).exists() else None
        launch_id = digest({"host": self.host_id, "argv": list(args), "cwd": str(cwd), "required": list(required)})
        if missing:
            return RuntimeResolution(
                RESOLUTION_SCHEMA, self.host_id, self.adapter_version, launch_id, "BLOCKED",
                _facts(RuntimeFact("executable", requested_exe, resolved_exe, None, "UNVERIFIED")),
                required, None, None, None, "unsupported-required-capability:" + ",".join(missing),
            )
        env = dict(environment) if environment is not None else os.environ.copy()
        try:
            proc = subprocess.run(
                args,
                cwd=cwd,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_seconds,
                check=False,
                shell=False,
            )
        except (FileNotFoundError, PermissionError, OSError) as exc:
            return RuntimeResolution(
                RESOLUTION_SCHEMA, self.host_id, self.adapter_version, launch_id, "BLOCKED",
                _facts(RuntimeFact("executable", requested_exe, resolved_exe, None, "UNVERIFIED")),
                required, None, None, None, f"launch-unavailable:{type(exc).__name__}",
            )
        except subprocess.TimeoutExpired as exc:
            out = exc.stdout or b""
            err = exc.stderr or b""
            return RuntimeResolution(
                RESOLUTION_SCHEMA, self.host_id, self.adapter_version, launch_id, "BLOCKED",
                _facts(RuntimeFact("executable", requested_exe, resolved_exe, resolved_exe, "OBSERVED" if resolved_exe else "UNVERIFIED")),
                required, None, _sha256_bytes(out), _sha256_bytes(err), "timeout",
            )
        observed_exe = resolved_exe
        outcome = "PASS" if proc.returncode == 0 else "FAILED"
        return RuntimeResolution(
            RESOLUTION_SCHEMA, self.host_id, self.adapter_version, launch_id, outcome,
            _facts(
                RuntimeFact("executable", requested_exe, resolved_exe, observed_exe, "OBSERVED" if observed_exe else "UNVERIFIED"),
                RuntimeFact("cwd", str(cwd), str(cwd), str(cwd), "OBSERVED"),
            ),
            required, proc.returncode, _sha256_bytes(proc.stdout), _sha256_bytes(proc.stderr),
            None if outcome == "PASS" else f"exit-code:{proc.returncode}",
        )

    def qualify(self) -> HostQualification:
        with tempfile.TemporaryDirectory(prefix="harness-rig-host-") as td:
            root = Path(td).resolve()
            script = (
                "import json,os,sys; "
                "print(json.dumps({'pid':os.getpid(),'ppid':os.getppid(),'executable':sys.executable,'cwd':os.getcwd(),"
                "'isolated':bool(sys.flags.isolated),'no_site':bool(sys.flags.no_site)}))"
            )
            env = {"PATH": os.defpath, "PYTHONNOUSERSITE": "1"}
            result = self.launch(
                (sys.executable, "-I", "-S", "-c", script),
                cwd=root,
                required_capabilities=("clean_process", "process_launch", "runtime_identity_observation"),
                environment=env,
            )
            reasons: list[str] = []
            if result.outcome != "PASS":
                reasons.append("clean-process-launch-failed")
            # The probe payload is deliberately re-run here to retain an observed runtime identity
            # rather than infer it from adapter configuration.
            observed: dict[str, object] | None = None
            try:
                probe = subprocess.run(
                    (sys.executable, "-I", "-S", "-c", script), cwd=root, env=env,
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    timeout=10, check=False, shell=False,
                )
                if probe.returncode == 0:
                    observed = json.loads(probe.stdout.decode("utf-8"))
            except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, UnicodeDecodeError):
                observed = None
            if not observed:
                reasons.append("runtime-identity-unobserved")
            else:
                if Path(str(observed.get("cwd", ""))).resolve() != root:
                    reasons.append("wrong-observed-cwd")
                if not observed.get("isolated") or not observed.get("no_site"):
                    reasons.append("probe-not-isolated")
                if Path(str(observed.get("executable", ""))).resolve() != Path(sys.executable).resolve():
                    reasons.append("wrong-runtime-executable")
            caps = self.capabilities()
            outcome = "PASS" if not reasons else "BLOCKED"
            identity_material = {
                "schema": QUALIFICATION_SCHEMA,
                "host_id": self.host_id,
                "adapter_version": self.adapter_version,
                "adapter_maturity": self.adapter_maturity,
                "outcome": outcome,
                "capabilities": asdict(caps),
                "runtime": {
                    "executable": str(Path(sys.executable).resolve()),
                    "python_version": sys.version.split()[0],
                    "os_name": os.name,
                    "isolated_probe": bool(observed and observed.get("isolated")),
                    "no_site_probe": bool(observed and observed.get("no_site")),
                },
                "reasons": reasons,
            }
            return HostQualification(
                QUALIFICATION_SCHEMA, self.host_id, self.adapter_version, self.adapter_maturity,
                outcome, caps, result, tuple(reasons), digest(identity_material),
            )


def qualification_to_json(qualification: HostQualification) -> str:
    return json.dumps(asdict(qualification), indent=2, sort_keys=True) + "\n"
