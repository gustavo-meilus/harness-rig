from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .canonical import digest


@dataclass(frozen=True)
class AuthorizationGrant:
    schema: str
    grant_id: str
    issuer: str
    principal: str
    action: str
    resource: str
    authority_id: str | None
    state_id: str | None
    subject_ref: str | None
    issued_at: str
    expires_at: str | None
    delegation: str
    origin: str

    @classmethod
    def issue(
        cls,
        *,
        issuer: str,
        principal: str,
        action: str,
        resource: str,
        authority_id: str | None = None,
        state_id: str | None = None,
        subject_ref: str | None = None,
        issued_at: str,
        expires_at: str | None = None,
        delegation: str = "none",
        origin: str = "interactive",
    ) -> "AuthorizationGrant":
        material = {
            "schema": "harness-rig/authorization-grant/experimental-v1",
            "issuer": issuer,
            "principal": principal,
            "action": action,
            "resource": resource,
            "authority_id": authority_id,
            "state_id": state_id,
            "subject_ref": subject_ref,
            "issued_at": issued_at,
            "expires_at": expires_at,
            "delegation": delegation,
            "origin": origin,
        }
        return cls(grant_id=digest(material), **material)


@dataclass(frozen=True)
class GrantValidation:
    outcome: str
    reason: str


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def validate_grant(
    grant: AuthorizationGrant | None,
    *,
    principal: str,
    action: str,
    resource: str,
    authority_id: str,
    state_id: str,
    subject_ref: str,
    now: str,
    trusted_issuers: set[str],
) -> GrantValidation:
    if grant is None:
        return GrantValidation("UNVERIFIABLE", "missing-grant")
    if grant.issuer not in trusted_issuers:
        return GrantValidation("INVALID", "untrusted-issuer")
    if grant.principal != principal:
        if grant.delegation == "none":
            return GrantValidation("INVALID", "principal-mismatch-nondelegable")
        return GrantValidation("INVALID", "principal-mismatch")
    if grant.action != action:
        return GrantValidation("INVALID", "action-mismatch")
    if grant.resource != resource:
        return GrantValidation("INVALID", "resource-mismatch")
    if grant.authority_id is not None and grant.authority_id != authority_id:
        return GrantValidation("INVALID", "authority-binding-mismatch")
    if grant.state_id is not None and grant.state_id != state_id:
        return GrantValidation("INVALID", "state-binding-mismatch")
    if grant.subject_ref is not None and grant.subject_ref != subject_ref:
        return GrantValidation("INVALID", "subject-binding-mismatch")
    now_i = _instant(now)
    if now_i < _instant(grant.issued_at):
        return GrantValidation("INVALID", "not-yet-valid")
    if grant.expires_at is not None and now_i >= _instant(grant.expires_at):
        return GrantValidation("INVALID", "expired")
    return GrantValidation("VALID", "valid")
