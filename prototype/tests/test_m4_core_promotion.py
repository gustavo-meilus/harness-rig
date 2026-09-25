from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from dataclasses import asdict, fields
from pathlib import Path

from harness_rig.acceptance import evaluate_acceptance
from harness_rig.assurance import AssurancePlan, AssuranceRequirement
from harness_rig.authority import (
    AUTHORITY_REF_SCHEMA,
    AuthorityRef,
    DirectAuthority,
    load_authority_ref,
)
from harness_rig.authorization import (
    AUTHORIZATION_GRANT_SCHEMA,
    LEGACY_AUTHORIZATION_GRANT_SCHEMA,
    AuthorizationGrant,
    load_authorization_grant,
    validate_grant,
)
from harness_rig.canonical import digest
from harness_rig.evidence import EvidenceReceipt
from harness_rig.gate import CommandGate, GateRequest
from harness_rig.state import (
    LEGACY_STATE_IDENTITY_SCHEMA,
    STATE_IDENTITY_SCHEMA,
    StateIdentity,
    capture_state,
    load_state_identity,
)
from harness_rig.topology import DirectTopology


NOW = "2026-09-25T12:00:00Z"
ISSUED = "2026-09-25T11:00:00Z"
FUTURE = "2026-09-25T13:00:00Z"


def run_git(repo: Path, *args: str) -> None:
    p = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
    if p.returncode != 0:
        raise AssertionError(p.stderr)


class HarnessRigM4Tests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory(prefix="hr-m4-")
        self.repo = Path(self.td.name) / "repo"
        self.repo.mkdir()
        run_git(self.repo, "init", "-b", "main")
        run_git(self.repo, "config", "user.name", "Harness Rig Test")
        run_git(self.repo, "config", "user.email", "harness-rig@example.invalid")
        (self.repo / "AUTHORITY.md").write_text("authority v1\n", encoding="utf-8")
        (self.repo / "app.txt").write_text("hello\n", encoding="utf-8")
        run_git(self.repo, "add", "-A")
        run_git(self.repo, "commit", "-m", "initial")

    def tearDown(self):
        self.td.cleanup()

    def authority(self) -> AuthorityRef:
        return DirectAuthority.from_file(self.repo, "AUTHORITY.md", "repository")

    def state(self) -> StateIdentity:
        return capture_state(self.repo, "test-repo")

    def plan(self, *, decision: str = "merge", version: str = "experimental-v1") -> AssurancePlan:
        return AssurancePlan.single(
            subject_ref="repository",
            requirement=AssuranceRequirement(
                claim_id="project.command",
                gate_id="command/test",
                gate_contract_version=version,
                decision_for=decision,
                require_authorization=True,
            ),
        )

    def grant(self, *, action: str = "merge") -> AuthorizationGrant:
        authority = self.authority()
        state = self.state()
        return AuthorizationGrant.issue(
            issuer="local-authority",
            principal="local-controller",
            action=action,
            resource="repository",
            authority_id=authority.authority_id,
            state_id=state.state_id,
            subject_ref="repository",
            issued_at=ISSUED,
            expires_at=FUTURE,
        )

    def receipt(self, authority: AuthorityRef | None = None) -> EvidenceReceipt:
        return CommandGate.run(GateRequest(
            repo=self.repo,
            repository_id="test-repo",
            claim_id="project.command",
            subject_ref="repository",
            authority=authority or self.authority(),
            run_id="m4-run",
            producer_id="m4-test",
            argv=(sys.executable, "-S", "-c", "print('ok')"),
        ))

    def accept(self, receipt: EvidenceReceipt | None, grant: AuthorizationGrant | None):
        return evaluate_acceptance(
            repo=self.repo,
            authority=self.authority(),
            current_state=self.state(),
            plan=self.plan(),
            receipt=receipt,
            grant=grant,
            principal="local-controller",
            run_id="m4-run",
            now=NOW,
            trusted_issuers={"local-authority"},
            resource="repository",
        )

    # M4-T01 / M4-V01 / M4-V02 / M4-V05
    def test_authority_ref_promoted_provider_neutral_shape_serves_gate_and_acceptance(self):
        authority = self.authority()
        self.assertEqual(authority.schema, AUTHORITY_REF_SCHEMA)
        self.assertEqual(
            {f.name for f in fields(AuthorityRef)},
            {"schema", "provider", "subject_ref", "authority_id"},
        )
        receipt = self.receipt(authority)
        grant = self.grant()
        verdict = self.accept(receipt, grant)
        self.assertEqual(receipt.authority_id, authority.authority_id)
        self.assertEqual(verdict.outcome, "ACCEPTED")

    def test_authority_ref_legacy_migration_drops_provider_local_fields_and_preserves_identity(self):
        content_digest = digest("authority body")
        legacy = {
            "provider": "direct-file/v1",
            "subject_ref": "repository",
            "source_path": "AUTHORITY.md",
            "content_digest": content_digest,
        }
        legacy["authority_id"] = digest(legacy)
        migrated = load_authority_ref(legacy)
        self.assertEqual(migrated.authority_id, legacy["authority_id"])
        self.assertNotIn("source_path", asdict(migrated))
        self.assertNotIn("content_digest", asdict(migrated))
        self.assertEqual(load_authority_ref(asdict(migrated)), migrated)

    def test_authority_ref_unknown_version_and_tampered_legacy_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "unsupported-authority-ref-schema"):
            load_authority_ref({
                "schema": "harness-rig/authority-ref/v2",
                "provider": "x",
                "subject_ref": "repository",
                "authority_id": "sha256:" + "0" * 64,
            })
        legacy = {
            "provider": "direct-file/v1",
            "subject_ref": "repository",
            "source_path": "AUTHORITY.md",
            "content_digest": "sha256:" + "1" * 64,
            "authority_id": "sha256:" + "2" * 64,
        }
        with self.assertRaisesRegex(ValueError, "legacy-integrity"):
            load_authority_ref(legacy)

    # M4-T02 / M4-V01 / M4-V05
    def test_authorization_grant_promoted_bounded_shape_and_integrity(self):
        grant = self.grant()
        self.assertEqual(grant.schema, AUTHORIZATION_GRANT_SCHEMA)
        self.assertNotIn("origin", asdict(grant))
        self.assertEqual(grant.recompute_grant_id(), grant.grant_id)
        validation = validate_grant(
            grant,
            principal="local-controller",
            action="merge",
            resource="repository",
            authority_id=self.authority().authority_id,
            state_id=self.state().state_id,
            subject_ref="repository",
            now=NOW,
            trusted_issuers={"local-authority"},
        )
        self.assertEqual(validation.outcome, "VALID")

    def test_authorization_grant_legacy_migration_is_deterministic(self):
        authority = self.authority()
        state = self.state()
        legacy_material = {
            "schema": LEGACY_AUTHORIZATION_GRANT_SCHEMA,
            "issuer": "local-authority",
            "principal": "local-controller",
            "action": "merge",
            "resource": "repository",
            "authority_id": authority.authority_id,
            "state_id": state.state_id,
            "subject_ref": "repository",
            "issued_at": ISSUED,
            "expires_at": FUTURE,
            "delegation": "none",
            "origin": "interactive",
        }
        legacy = {"grant_id": digest(legacy_material), **legacy_material}
        migrated_a = load_authorization_grant(legacy)
        migrated_b = load_authorization_grant(legacy)
        self.assertEqual(migrated_a, migrated_b)
        self.assertEqual(migrated_a.schema, AUTHORIZATION_GRANT_SCHEMA)
        self.assertNotEqual(migrated_a.grant_id, legacy["grant_id"])
        self.assertEqual(load_authorization_grant(asdict(migrated_a)), migrated_a)

    def test_authorization_grant_unknown_version_tamper_and_unimplemented_delegation_fail_closed(self):
        grant = self.grant()
        unknown = {**asdict(grant), "schema": "harness-rig/authorization-grant/v2"}
        with self.assertRaisesRegex(ValueError, "unsupported-authorization-grant-schema"):
            load_authorization_grant(unknown)
        tampered = {**asdict(grant), "action": "deploy"}
        with self.assertRaisesRegex(ValueError, "integrity"):
            load_authorization_grant(tampered)
        with self.assertRaisesRegex(ValueError, "unsupported-delegation"):
            AuthorizationGrant.issue(
                issuer="local-authority",
                principal="p",
                action="merge",
                resource="repository",
                issued_at=ISSUED,
                delegation="subgrant",
            )

    # M4-T03 / M4-V01 / M4-V05
    def test_state_identity_promoted_stable_round_trip(self):
        state = self.state()
        self.assertEqual(state.schema, STATE_IDENTITY_SCHEMA)
        self.assertEqual(state.recompute_state_id(), state.state_id)
        self.assertEqual(load_state_identity(asdict(state)), state)

    def test_state_identity_legacy_migration_rekeys_state_id_deterministically(self):
        current = asdict(self.state())
        legacy = {**current, "schema": LEGACY_STATE_IDENTITY_SCHEMA}
        legacy_material = {key: value for key, value in legacy.items() if key != "state_id"}
        legacy["state_id"] = digest(legacy_material)
        migrated_a = load_state_identity(legacy)
        migrated_b = load_state_identity(legacy)
        self.assertEqual(migrated_a, migrated_b)
        self.assertEqual(migrated_a.schema, STATE_IDENTITY_SCHEMA)
        self.assertNotEqual(migrated_a.state_id, legacy["state_id"])
        self.assertEqual(migrated_a.content_id, legacy["content_id"])

    def test_state_identity_unknown_version_and_tamper_fail_closed(self):
        state = asdict(self.state())
        with self.assertRaisesRegex(ValueError, "unsupported-state-identity-schema"):
            load_state_identity({**state, "schema": "harness-rig/state-identity/v2"})
        state["repository_id"] = "other"
        with self.assertRaisesRegex(ValueError, "integrity"):
            load_state_identity(state)

    def test_state_identity_stable_golden_vector(self):
        material = {
            "schema": STATE_IDENTITY_SCHEMA,
            "repository_id": "repo-golden",
            "revision": {"head_oid": "abc123", "head_tree_oid": "def456"},
            "index_manifest_digest": "sha256:" + "1" * 64,
            "tracked_manifest_digest": "sha256:" + "2" * 64,
            "untracked_nonignored_manifest_digest": "sha256:" + "3" * 64,
            "submodules": [],
            "content_id": "sha256:" + "4" * 64,
        }
        serialized = {**material, "state_id": digest(material)}
        loaded = load_state_identity(serialized)
        self.assertEqual(
            loaded.state_id,
            "sha256:34acc8b66fe721893eed77614b5f5797663eb37df5f908b058fd9d9a5c1610f5",
        )

    # M4-T04 / M4-T05: deliberately not promoted.
    def test_receipt_and_verdict_remain_experimental_after_m4(self):
        receipt = self.receipt()
        verdict = self.accept(receipt, self.grant())
        self.assertEqual(receipt.schema, "harness-rig/evidence-receipt/experimental-v1")
        self.assertEqual(verdict.schema, "harness-rig/acceptance-verdict/experimental-v1")

    # M4-T06 / M4-V03
    def test_assurance_plan_has_no_worker_or_host_selection_surface(self):
        self.assertEqual(
            {f.name for f in fields(AssurancePlan)},
            {"schema", "subject_ref", "requirement"},
        )
        self.assertFalse(any(name in {"worker", "host", "model", "principal"} for name in (f.name for f in fields(AssuranceRequirement))))

    # M4-T06 / M4-V04
    def test_topology_cannot_waive_required_evidence(self):
        topology = DirectTopology.direct("local-controller")
        self.assertEqual(topology.formation, "direct-single-process")
        verdict = self.accept(None, self.grant())
        self.assertEqual(verdict.outcome, "BLOCKED")
        self.assertIn("missing-required-receipt", verdict.reasons)

    def test_topology_cannot_broaden_authorization_and_technical_formation_is_not_authorization(self):
        topology = DirectTopology.direct("local-controller")
        self.assertEqual(
            {f.name for f in fields(DirectTopology)},
            {"schema", "principal", "formation"},
        )
        invalid_grant = self.grant(action="deploy")
        verdict = self.accept(self.receipt(), invalid_grant)
        self.assertEqual(verdict.outcome, "BLOCKED")
        self.assertIn("authorization-invalid:action-mismatch", verdict.reasons)

        no_grant = self.accept(self.receipt(), None)
        self.assertEqual(no_grant.outcome, "BLOCKED")
        self.assertIn("authorization-unverifiable:missing-grant", no_grant.reasons)

    # M4-V02
    def test_stable_core_has_no_provider_escape_bags(self):
        for cls in (AuthorityRef, AuthorizationGrant, StateIdentity):
            names = {f.name for f in fields(cls)}
            self.assertTrue(names.isdisjoint({"extra", "extras", "metadata", "provider_data", "extensions"}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
