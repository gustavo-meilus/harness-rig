from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .canonical import digest, sha256_bytes


@dataclass(frozen=True)
class AuthorityRef:
    provider: str
    subject_ref: str
    source_path: str
    content_digest: str
    authority_id: str


class DirectAuthority:
    """Direct file-backed authority provider for the M3 vertical slice."""

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
        material = {
            "provider": cls.provider,
            "subject_ref": subject_ref,
            "source_path": relative_path.replace("\\", "/"),
            "content_digest": content_digest,
        }
        return AuthorityRef(
            provider=cls.provider,
            subject_ref=subject_ref,
            source_path=material["source_path"],
            content_digest=content_digest,
            authority_id=digest(material),
        )
