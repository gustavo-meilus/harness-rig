"""Harness Rig r8.10 prototype: trust identities plus bounded verification providers."""

from .authority import AuthorityRef, DirectAuthority, DirectAuthorityProvider, load_authority_ref
from .authorization import AuthorizationGrant, GrantValidation, load_authorization_grant
from .state import StateIdentity, capture_state, load_state_identity
from .assurance import AssuranceRequirement, AssurancePlan
from .topology import DirectTopology
from .evidence import EvidenceReceipt
from .gate import CommandGate, GateRequest, GateClaim, GateOutcome
from .acceptance import AcceptanceVerdict, evaluate_acceptance
from .vertical import VerticalSliceRequest, VerticalSliceResult, run_vertical_slice
from .spec_engine import SpecEngine, SpecEngineHealth, SpecArchiveMutation
from .openspec import OpenSpecAdapter, OpenSpecAuthoritySnapshot, GuardedArchiveResult, guarded_archive
from .architecture_gate import ArchitectureGate, ArchitecturePolicy, ArchitectureRule, evaluate_architecture
from .playwright_gate import PlaywrightGate, RequiredScenario, RuntimeObservation, evaluate_playwright_report
from .mutation_gate import MutationCase, MutationResult, run_mutation_case, validate_mutation_map
from .product import CliEnvelope, ProductConfig, load_cli_envelope, load_effective_config
from .migration import MigrationAssessment, MigrationState, assess_migration, apply_migration, rollback_migration
from .release import ReleaseArtifact, ReleaseRecord, build_release_record, verify_release_record
from .host import (
    CapabilityClaim, CapabilitySet, RuntimeFact, RuntimeResolution, HostQualification,
    FreshVerifierBoundary, FreshVerifierEligibility, LocalProcessHost, evaluate_fresh_verifier,
)

__all__ = [
    "AuthorityRef", "DirectAuthority", "DirectAuthorityProvider", "load_authority_ref",
    "AuthorizationGrant", "GrantValidation", "load_authorization_grant",
    "StateIdentity", "capture_state", "load_state_identity",
    "AssuranceRequirement", "AssurancePlan",
    "DirectTopology",
    "EvidenceReceipt",
    "CommandGate", "GateRequest", "GateClaim", "GateOutcome",
    "AcceptanceVerdict", "evaluate_acceptance",
    "VerticalSliceRequest", "VerticalSliceResult", "run_vertical_slice",
    "SpecEngine", "SpecEngineHealth", "SpecArchiveMutation",
    "OpenSpecAdapter", "OpenSpecAuthoritySnapshot", "GuardedArchiveResult", "guarded_archive",
    "ArchitectureGate", "ArchitecturePolicy", "ArchitectureRule", "evaluate_architecture",
    "PlaywrightGate", "RequiredScenario", "RuntimeObservation", "evaluate_playwright_report",
    "MutationCase", "MutationResult", "run_mutation_case", "validate_mutation_map",
    "CliEnvelope", "ProductConfig", "load_cli_envelope", "load_effective_config",
    "MigrationAssessment", "MigrationState", "assess_migration", "apply_migration", "rollback_migration",
    "ReleaseArtifact", "ReleaseRecord", "build_release_record", "verify_release_record",
    "CapabilityClaim", "CapabilitySet", "RuntimeFact", "RuntimeResolution", "HostQualification",
    "FreshVerifierBoundary", "FreshVerifierEligibility", "LocalProcessHost", "evaluate_fresh_verifier",
]
