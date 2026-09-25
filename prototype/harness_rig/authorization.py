from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .canonical import digest, is_sha256_digest


AUTHORIZATION_GRANT_SCHEMA = "harness-rig/authorization-grant/v1"
LEGACY_AUTHORIZATION_GRANT_SCHEMA = "harness-rig/authorization-grant/experimental-v1"


@dataclass(frozen=True)
class AuthorizationGrant:
    """Stable bounded authorization grant.

    Provider credentials, revocation databases, and provider-specific status are
    deliberately not embedded in this shared value. Action-time callers still
    own any authoritative provider-current-status check they require.
    """

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
    ) -> "AuthorizationGrant":
        if delegation != "none":
            raise ValueError("unsupported-delegation")
        issued = _instant(issued_at)
        if expires_at is not None and _instant(expires_at) <= issued:
            raise ValueError("invalid-grant-lifetime")
        material = {
            "schema": AUTHORIZATION_GRANT_SCHEMA,
            "issuer": _required(issuer, "issuer"),
            "principal": _required(principal, "principal"),
            "action": _required(action, "action"),
            "resource": _required(resource, "resource"),
            "authority_id": _optional_digest(authority_id, "authority-id"),
            "state_id": _optional_digest(state_id, "state-id"),
            "subject_ref": _optional_string(subject_ref, "subject-ref"),
            "issued_at": issued_at,
            "expires_at": expires_at,
            "delegation": delegation,
        }
        return cls(grant_id=digest(material), **material)

    def recompute_grant_id(self) -> str:
        return digest(_grant_material(self))


@dataclass(frozen=True)
class GrantValidation:
    outcome: str
    reason: str


def _required(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"invalid-grant-{field}")
    return value


def _optional_string(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _required(value, field)


def _optional_digest(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not is_sha256_digest(value):
        raise ValueError(f"invalid-grant-{field}")
    return value


def _instant(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("invalid-timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _grant_material(grant: AuthorizationGrant) -> dict[str, Any]:
    return {
        "schema": grant.schema,
        "issuer": grant.issuer,
        "principal": grant.principal,
        "action": grant.action,
        "resource": grant.resource,
        "authority_id": grant.authority_id,
        "state_id": grant.state_id,
        "subject_ref": grant.subject_ref,
        "issued_at": grant.issued_at,
        "expires_at": grant.expires_at,
        "delegation": grant.delegation,
    }


def load_authorization_grant(data: dict[str, Any]) -> AuthorizationGrant:
    """Load stable v1 or migrate the exact M3 experimental v1 serialized form."""

    if not isinstance(data, dict):
        raise ValueError("invalid-authorization-grant")

    stable_fields = {
        "schema", "grant_id", "issuer", "principal", "action", "resource",
        "authority_id", "state_id", "subject_ref", "issued_at", "expires_at", "delegation",
    }
    legacy_fields = stable_fields | {"origin"}
    schema = data.get("schema")

    if schema == AUTHORIZATION_GRANT_SCHEMA:
        if set(data) != stable_fields:
            raise ValueError("invalid-authorization-grant-fields")
        grant = AuthorizationGrant(
            schema=schema,
            grant_id=_required(data["grant_id"], "grant-id"),
            issuer=_required(data["issuer"], "issuer"),
            principal=_required(data["principal"], "principal"),
            action=_required(data["action"], "action"),
            resource=_required(data["resource"], "resource"),
            authority_id=_optional_digest(data["authority_id"], "authority-id"),
            state_id=_optional_digest(data["state_id"], "state-id"),
            subject_ref=_optional_string(data["subject_ref"], "subject-ref"),
            issued_at=_required(data["issued_at"], "issued-at"),
            expires_at=_optional_string(data["expires_at"], "expires-at"),
            delegation=_required(data["delegation"], "delegation"),
        )
        if grant.delegation != "none":
            raise ValueError("unsupported-delegation")
        issued = _instant(grant.issued_at)
        if grant.expires_at is not None and _instant(grant.expires_at) <= issued:
            raise ValueError("invalid-grant-lifetime")
        if not is_sha256_digest(grant.grant_id) or grant.recompute_grant_id() != grant.grant_id:
            raise ValueError("invalid-authorization-grant-integrity")
        return grant

    if schema == LEGACY_AUTHORIZATION_GRANT_SCHEMA:
        if set(data) != legacy_fields:
            raise ValueError("invalid-legacy-authorization-grant-fields")
        legacy_material = {key: data[key] for key in legacy_fields if key != "grant_id"}
        legacy_id = data.get("grant_id")
        if not is_sha256_digest(legacy_id) or digest(legacy_material) != legacy_id:
            raise ValueError("invalid-legacy-authorization-grant-integrity")
        if data["delegation"] != "none":
            raise ValueError("unsupported-delegation")
        return AuthorizationGrant.issue(
            issuer=data["issuer"],
            principal=data["principal"],
            action=data["action"],
            resource=data["resource"],
            authority_id=data["authority_id"],
            state_id=data["state_id"],
            subject_ref=data["subject_ref"],
            issued_at=data["issued_at"],
            expires_at=data["expires_at"],
            delegation=data["delegation"],
        )

    raise ValueError("unsupported-authorization-grant-schema")


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
    if grant.schema != AUTHORIZATION_GRANT_SCHEMA:
        return GrantValidation("INVALID", "unsupported-schema")
    if not is_sha256_digest(grant.grant_id) or grant.recompute_grant_id() != grant.grant_id:
        return GrantValidation("INVALID", "integrity-failure")
    if grant.delegation != "none":
        return GrantValidation("INVALID", "unsupported-delegation")
    if grant.issuer not in trusted_issuers:
        return GrantValidation("INVALID", "untrusted-issuer")
    if grant.principal != principal:
        return GrantValidation("INVALID", "principal-mismatch-nondelegable")
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
    try:
        now_i = _instant(now)
        issued_i = _instant(grant.issued_at)
        expires_i = _instant(grant.expires_at) if grant.expires_at is not None else None
    except (TypeError, ValueError):
        return GrantValidation("INVALID", "invalid-time")
    if expires_i is not None and expires_i <= issued_i:
        return GrantValidation("INVALID", "invalid-lifetime")
    if now_i < issued_i:
        return GrantValidation("INVALID", "not-yet-valid")
    if expires_i is not None and now_i >= expires_i:
        return GrantValidation("INVALID", "expired")
    return GrantValidation("VALID", "valid")
