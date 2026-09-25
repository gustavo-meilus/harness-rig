from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

from harness_rig.cli import main as cli_main
from harness_rig.host import (
    CapabilityClaim,
    FreshVerifierBoundary,
    HostError,
    LocalProcessHost,
    evaluate_fresh_verifier,
)


class HarnessRigM8HostCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.host = LocalProcessHost()

    def test_t01_first_stable_host_candidate_has_only_earned_claims(self):
        caps = self.host.capabilities()
        self.assertEqual(caps.host_id, "local-subprocess")
        self.assertEqual(caps.adapter_maturity, "STABLE")
        for capability in ("clean_process", "process_launch", "runtime_identity_observation", "crash_reconciliation"):
            self.assertTrue(caps.supports(capability))
            self.assertEqual(caps.claim(capability).maturity, "STABLE")
            self.assertTrue(caps.claim(capability).evidence)
        for capability in ("fresh_verifier", "isolated_worker", "read_only_worker", "worktree_worker", "permission_enforcement", "isolated_writer"):
            self.assertFalse(caps.supports(capability))
            self.assertEqual(caps.claim(capability).maturity, "UNSUPPORTED")
            self.assertEqual(caps.claim(capability).evidence, ())

    def test_t02_maturity_distinction_is_explicit_and_fail_closed(self):
        with self.assertRaises(HostError):
            CapabilityClaim("x", "STABLE", False)
        with self.assertRaises(HostError):
            CapabilityClaim("x", "UNSUPPORTED", True)
        with self.assertRaises(HostError):
            CapabilityClaim("x", "INVENTED", True)

    def test_v01_clean_process_discovery_and_launch_pass(self):
        qualification = self.host.qualify()
        self.assertEqual(qualification.outcome, "PASS")
        self.assertEqual(qualification.adapter_maturity, "STABLE")
        self.assertEqual(qualification.clean_process.outcome, "PASS")
        self.assertEqual(qualification.clean_process.exit_code, 0)
        self.assertEqual(qualification.reasons, ())
        facts = {fact.key: fact for fact in qualification.clean_process.facts}
        self.assertEqual(facts["executable"].requested, sys.executable)
        self.assertEqual(Path(facts["executable"].resolved).resolve(), Path(sys.executable).resolve())
        self.assertEqual(Path(facts["executable"].observed).resolve(), Path(sys.executable).resolve())
        self.assertEqual(facts["executable"].status, "OBSERVED")

    def test_doctor_runs_fresh_probe_and_emits_machine_readable_qualification(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = cli_main(["doctor"])
        self.assertEqual(rc, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["schema"], "harness-rig/host-qualification/v1")
        self.assertEqual(payload["host_id"], "local-subprocess")
        self.assertEqual(payload["outcome"], "PASS")
        self.assertTrue(payload["qualification_id"])

    def test_v02_requested_resolved_observed_facts_are_not_collapsed(self):
        with tempfile.TemporaryDirectory() as td:
            result = self.host.launch(
                (sys.executable, "-I", "-S", "-c", "print('ok')"),
                cwd=Path(td),
                required_capabilities=("process_launch", "runtime_identity_observation"),
            )
        self.assertEqual(result.outcome, "PASS")
        facts = {fact.key: fact for fact in result.facts}
        self.assertEqual(facts["executable"].requested, sys.executable)
        self.assertEqual(facts["executable"].resolved, facts["executable"].observed)
        self.assertEqual(facts["cwd"].requested, facts["cwd"].observed)
        self.assertIsNotNone(result.stdout_digest)
        self.assertIsNotNone(result.stderr_digest)

    def test_v03_required_read_only_isolation_or_unknown_capability_blocks_before_launch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            marker = root / "ran.txt"
            code = f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')"
            for required in ("read_only_worker", "isolated_worker", "does_not_exist"):
                result = self.host.launch((sys.executable, "-c", code), cwd=root, required_capabilities=(required,))
                self.assertEqual(result.outcome, "BLOCKED")
                self.assertIn("unsupported-required-capability", result.reason)
                self.assertFalse(marker.exists())

    def test_t04_fresh_verifier_requires_nonownership_distinct_context_and_real_read_only_boundary(self):
        eligible = evaluate_fresh_verifier(FreshVerifierBoundary(
            implementer_id="writer-1", verifier_id="verifier-1",
            implementer_context_id="ctx-w", verifier_context_id="ctx-v",
            verifier_owned_batch=False, read_only_required=True, read_only_enforced=True,
        ))
        self.assertEqual(eligible.outcome, "ELIGIBLE")
        self.assertEqual(eligible.reasons, ())

        blocked = evaluate_fresh_verifier(FreshVerifierBoundary(
            implementer_id="writer-1", verifier_id="writer-1",
            implementer_context_id="ctx", verifier_context_id="ctx",
            verifier_owned_batch=True, read_only_required=True, read_only_enforced=False,
        ))
        self.assertEqual(blocked.outcome, "BLOCKED")
        self.assertIn("verifier-is-implementer", blocked.reasons)
        self.assertIn("shared-context", blocked.reasons)
        self.assertIn("verifier-owned-batch", blocked.reasons)
        self.assertIn("read-only-not-enforced", blocked.reasons)

    def test_fresh_verifier_is_not_equivalent_to_different_label_only(self):
        result = evaluate_fresh_verifier(FreshVerifierBoundary(
            implementer_id="writer", verifier_id="reviewer",
            implementer_context_id="same", verifier_context_id="same",
            verifier_owned_batch=False, read_only_required=False, read_only_enforced=False,
        ))
        self.assertEqual(result.outcome, "BLOCKED")
        self.assertIn("shared-context", result.reasons)

    def test_v04_crash_is_attributed_and_subsequent_reconciliation_launch_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            failed = self.host.launch(
                (sys.executable, "-I", "-S", "-c", "import sys; print('before-crash'); sys.exit(7)"),
                cwd=root,
            )
            self.assertEqual(failed.outcome, "FAILED")
            self.assertEqual(failed.exit_code, 7)
            self.assertEqual(failed.reason, "exit-code:7")
            self.assertTrue(failed.stdout_digest.startswith("sha256:"))
            self.assertTrue(failed.stderr_digest.startswith("sha256:"))

            recovered = self.host.launch(
                (sys.executable, "-I", "-S", "-c", "print('recovered')"),
                cwd=root,
                required_capabilities=("crash_reconciliation",),
            )
            self.assertEqual(recovered.outcome, "PASS")
            self.assertEqual(recovered.exit_code, 0)
            self.assertNotEqual(failed.launch_id, recovered.launch_id)

    def test_timeout_is_blocked_and_does_not_poison_next_launch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            timed = self.host.launch(
                (sys.executable, "-I", "-S", "-c", "import time; time.sleep(2)"),
                cwd=root,
                timeout_seconds=0.05,
            )
            self.assertEqual(timed.outcome, "BLOCKED")
            self.assertEqual(timed.reason, "timeout")
            recovered = self.host.launch((sys.executable, "-I", "-S", "-c", "pass"), cwd=root)
            self.assertEqual(recovered.outcome, "PASS")

    def test_launch_unavailable_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            result = self.host.launch(("/definitely/missing/harness-rig-host",), cwd=Path(td))
        self.assertEqual(result.outcome, "BLOCKED")
        self.assertIn("launch-unavailable", result.reason)

    def test_v05_isolated_writer_cannot_be_promoted_without_formal_native_evidence(self):
        with self.assertRaisesRegex(HostError, "isolated-writer-stable-requires-formal-native-evidence"):
            CapabilityClaim("isolated_writer", "STABLE", True, ("implemented-local",))
        admitted = CapabilityClaim("isolated_writer", "STABLE", True, ("formal-native:example-packet/v1",))
        self.assertTrue(admitted.supported)
        claim = self.host.capabilities().claim("isolated_writer")
        self.assertFalse(claim.supported)
        self.assertEqual(claim.maturity, "UNSUPPORTED")
        self.assertEqual(claim.evidence, ())
        with tempfile.TemporaryDirectory() as td:
            result = self.host.launch(
                (sys.executable, "-I", "-S", "-c", "pass"),
                cwd=Path(td), required_capabilities=("isolated_writer",),
            )
        self.assertEqual(result.outcome, "BLOCKED")

    def test_capability_is_technical_not_authorization(self):
        caps = self.host.capabilities()
        self.assertFalse(hasattr(caps, "grant"))
        self.assertFalse(hasattr(caps, "authorization"))
        self.assertFalse(hasattr(self.host, "authorize"))

    def test_qualification_id_is_deterministic_for_same_observed_shape(self):
        # Qualification includes digests rather than volatile PID output, so repeated probes
        # retain a stable identity when runtime facts and capability claims are unchanged.
        first = self.host.qualify()
        second = self.host.qualify()
        self.assertEqual(first.qualification_id, second.qualification_id)


if __name__ == "__main__":
    unittest.main()
