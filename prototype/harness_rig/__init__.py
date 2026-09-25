"""Harness Rig r8.8 prototype: trust identities, Context/OpenSpec, repository enforcement, and host qualification."""

from .authority import AuthorityRef, DirectAuthority, DirectAuthorityProvider, load_authority_ref
from .authorization import AuthorizationGrant, GrantValidation, load_authorization_grant
from .state import StateIdentity, capture_state, load_state_identity
from .assurance import AssuranceRequirement, AssurancePlan
from .topology import DirectTopology
from .evidence import EvidenceReceipt
from .gate import CommandGate, GateRequest
from .acceptance import AcceptanceVerdict, evaluate_acceptance
from .vertical import VerticalSliceRequest, VerticalSliceResult, run_vertical_slice
from .spec_engine import SpecEngine, SpecEngineHealth, SpecArchiveMutation
from .openspec import OpenSpecAdapter, OpenSpecAuthoritySnapshot, GuardedArchiveResult, guarded_archive
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
    "CommandGate", "GateRequest",
    "AcceptanceVerdict", "evaluate_acceptance",
    "VerticalSliceRequest", "VerticalSliceResult", "run_vertical_slice",
    "SpecEngine", "SpecEngineHealth", "SpecArchiveMutation",
    "OpenSpecAdapter", "OpenSpecAuthoritySnapshot", "GuardedArchiveResult", "guarded_archive",
    "CapabilityClaim", "CapabilitySet", "RuntimeFact", "RuntimeResolution", "HostQualification",
    "FreshVerifierBoundary", "FreshVerifierEligibility", "LocalProcessHost", "evaluate_fresh_verifier",
]
