from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .canonical import digest, is_sha256_digest, sha256_bytes


AUTHORITY_REF_SCHEMA = "harness-rig/authority-ref/v1"


@dataclass(frozen=True)
class AuthorityRef:
    """Stable provider-neutral identity for accepted authority."""

    schema: str
    provider: str
    subject_ref: str
    authority_id: str


def _require_nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"invalid-authority-ref-{field}")
    return value


def load_authority_ref(data: dict[str, Any]) -> AuthorityRef:
    """Load stable v1 or deterministically migrate the M3 direct-file shape.

    The M3 shape intentionally carried provider-local source_path/content_digest
    fields. Stable v1 drops those fields from the shared contract while preserving
    the provider-computed authority_id.
    """

    if not isinstance(data, dict):
        raise ValueError("invalid-authority-ref")

    stable_fields = {"schema", "provider", "subject_ref", "authority_id"}
    legacy_fields = {"provider", "subject_ref", "source_path", "content_digest", "authority_id"}

    if "schema" in data:
        if data.get("schema") != AUTHORITY_REF_SCHEMA:
            raise ValueError("unsupported-authority-ref-schema")
        if set(data) != stable_fields:
            raise ValueError("invalid-authority-ref-fields")
        provider = _require_nonempty(data["provider"], "provider")
        subject_ref = _require_nonempty(data["subject_ref"], "subject-ref")
        authority_id = _require_nonempty(data["authority_id"], "authority-id")
        if not is_sha256_digest(authority_id):
            raise ValueError("invalid-authority-ref-authority-id")
        return AuthorityRef(AUTHORITY_REF_SCHEMA, provider, subject_ref, authority_id)

    if set(data) != legacy_fields:
        raise ValueError("unsupported-authority-ref-legacy-shape")

    provider = _require_nonempty(data["provider"], "provider")
    subject_ref = _require_nonempty(data["subject_ref"], "subject-ref")
    source_path = _require_nonempty(data["source_path"], "source-path")
    content_digest = _require_nonempty(data["content_digest"], "content-digest")
    authority_id = _require_nonempty(data["authority_id"], "authority-id")
    if not is_sha256_digest(content_digest) or not is_sha256_digest(authority_id):
        raise ValueError("invalid-authority-ref-digest")

    expected = digest({
        "provider": provider,
        "subject_ref": subject_ref,
        "source_path": source_path,
        "content_digest": content_digest,
    })
    if authority_id != expected:
        raise ValueError("invalid-authority-ref-legacy-integrity")

    return AuthorityRef(AUTHORITY_REF_SCHEMA, provider, subject_ref, authority_id)


class DirectAuthority:
    """Direct file-backed authority provider.

    File path and content-digest mechanics are provider-local. Only the stable
    AuthorityRef crosses into gates/acceptance.
    """

    provider = "direct-file/v1"

    @classmethod
    def from_file(cls, repo_root: Path, relative_path: str, subject_ref: str = "repository") -> AuthorityRef:
        root = repo_root.resolve()
        path = (root / relative_path).resolve()
        if root not in [path, *path.parents]:
            raise ValueError("authority path escapes repository root")
        if not path.is_file():
            raise FileNotFoundError(path)
        content_digest = sha256_bytes(path.read_bytes())
        provider_material = {
            "provider": cls.provider,
            "subject_ref": subject_ref,
            "source_path": relative_path.replace("\\", "/"),
            "content_digest": content_digest,
        }
        return AuthorityRef(
            schema=AUTHORITY_REF_SCHEMA,
            provider=cls.provider,
            subject_ref=subject_ref,
            authority_id=digest(provider_material),
        )


class DirectAuthorityProvider:
    """Provider wrapper matching the M6 authority-provider vocabulary.

    The underlying direct-file identity and Stable AuthorityRef are unchanged;
    this class avoids changing the M3/M4 public surface while giving callers a
    provider-shaped entry point alongside OpenSpecAdapter.
    """

    provider = DirectAuthority.provider

    @classmethod
    def resolve(
        cls,
        repo_root: Path,
        relative_path: str,
        subject_ref: str = "repository",
    ) -> AuthorityRef:
        return DirectAuthority.from_file(repo_root, relative_path, subject_ref)
