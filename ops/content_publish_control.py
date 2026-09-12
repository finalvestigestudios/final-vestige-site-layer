#!/usr/bin/env python3
"""Fail-closed reference control plane for governed FinalVestige.com content publication.

This module intentionally contains no HTTP client and cannot publish to WordPress by itself.
It validates one immutable QD-cleared package, enforces an external page/post allowlist,
performs a single transactional resource mutation through an injected adapter, verifies the
destination, and records idempotency only after successful readback.

FVD-6 R1 is a control-layer artifact, not activation authority.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping, Protocol, Iterable

SPEC = "fvs-content-publish/v1"
PACKAGE_ID_RE = re.compile(r"[A-Z0-9][A-Z0-9._:-]{7,127}")
SHA256_RE = re.compile(r"[a-f0-9]{64}")

# Resource-local fields only. Global WordPress settings are deliberately absent.
MUTABLE_FIELDS = frozenset(
    {
        "title",
        "content",
        "excerpt",
        "featured_media",
        "slug",
        "status",
        "seo",
        "indexing",
    }
)
SNAPSHOT_FIELDS = tuple(sorted(MUTABLE_FIELDS))
ALLOWED_KINDS = frozenset({"post", "page"})
DISALLOWED_STATUSES = frozenset({"trash", "delete", "deleted", "auto-draft"})
ENVELOPE_KEYS = frozenset({"manifest", "package_sha256"})
MANIFEST_KEYS = frozenset(
    {
        "spec",
        "package_id",
        "qd_artifact_id",
        "qd_decision_id",
        "target",
        "expected_before_sha256",
        "authorized_fields",
        "mutation",
    }
)
TARGET_KEYS = frozenset({"kind", "id"})


class ContentPublishError(RuntimeError):
    """Base fail-closed control-plane error."""


class ValidationError(ContentPublishError):
    pass


class PolicyError(ContentPublishError):
    pass


class PreconditionError(ContentPublishError):
    pass


class ReplayConflict(ContentPublishError):
    pass


class VerificationError(ContentPublishError):
    pass


class CriticalRollbackFailure(ContentPublishError):
    pass


class ResourceAdapter(Protocol):
    def read(self, kind: str, resource_id: int) -> Mapping[str, Any]:
        ...

    def write(self, kind: str, resource_id: int, patch: Mapping[str, Any]) -> None:
        ...

    def restore(self, kind: str, resource_id: int, snapshot: Mapping[str, Any]) -> None:
        ...


class Ledger(Protocol):
    def get(self, package_id: str) -> Mapping[str, Any] | None:
        ...

    def put(self, package_id: str, record: Mapping[str, Any]) -> None:
        ...


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_package_hash(manifest: Mapping[str, Any]) -> str:
    return sha256_hex(_canonical_bytes(manifest))


def normalized_snapshot(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize all governed resource-local fields, including absent values.

    This deliberately fingerprints fields a package is not changing so status/slug/SEO/
    indexing drift is caught rather than silently overwritten or ignored.
    """
    if not isinstance(raw, Mapping):
        raise ValidationError("resource snapshot must be an object")
    return {field: raw.get(field) for field in SNAPSHOT_FIELDS}


def snapshot_hash(raw: Mapping[str, Any]) -> str:
    return sha256_hex(_canonical_bytes(normalized_snapshot(raw)))


def _require_exact_keys(value: Mapping[str, Any], expected: frozenset[str], label: str) -> None:
    keys = frozenset(value.keys())
    if keys != expected:
        missing = sorted(expected - keys)
        extra = sorted(keys - expected)
        raise ValidationError(f"{label} keys are not exact; missing={missing}, extra={extra}")


def validate_envelope(envelope: Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    if not isinstance(envelope, Mapping):
        raise ValidationError("package envelope must be an object")
    _require_exact_keys(envelope, ENVELOPE_KEYS, "envelope")

    manifest = envelope["manifest"]
    claimed_hash = envelope["package_sha256"]
    if not isinstance(manifest, Mapping):
        raise ValidationError("manifest must be an object")
    if not isinstance(claimed_hash, str) or not SHA256_RE.fullmatch(claimed_hash):
        raise ValidationError("package_sha256 must be lowercase SHA-256 hex")
    _require_exact_keys(manifest, MANIFEST_KEYS, "manifest")

    if manifest["spec"] != SPEC:
        raise ValidationError(f"unsupported spec: {manifest['spec']!r}")

    package_id = manifest["package_id"]
    if not isinstance(package_id, str) or not PACKAGE_ID_RE.fullmatch(package_id):
        raise ValidationError("package_id does not satisfy the immutable ID contract")

    for field in ("qd_artifact_id", "qd_decision_id"):
        value = manifest[field]
        if not isinstance(value, str) or not value.strip() or len(value) > 256:
            raise ValidationError(f"{field} must be a non-empty bounded string")

    target = manifest["target"]
    if not isinstance(target, Mapping):
        raise ValidationError("target must be an object")
    _require_exact_keys(target, TARGET_KEYS, "target")
    kind, resource_id = target["kind"], target["id"]
    if kind not in ALLOWED_KINDS:
        raise ValidationError("target kind must be page or post")
    if isinstance(resource_id, bool) or not isinstance(resource_id, int) or resource_id <= 0:
        raise ValidationError("target id must be a positive integer")

    before_hash = manifest["expected_before_sha256"]
    if not isinstance(before_hash, str) or not SHA256_RE.fullmatch(before_hash):
        raise ValidationError("expected_before_sha256 must be lowercase SHA-256 hex")

    authorized = manifest["authorized_fields"]
    if (
        not isinstance(authorized, list)
        or not authorized
        or any(not isinstance(x, str) for x in authorized)
        or len(set(authorized)) != len(authorized)
    ):
        raise ValidationError("authorized_fields must be a non-empty unique string list")
    authorized_set = frozenset(authorized)
    if not authorized_set <= MUTABLE_FIELDS:
        raise ValidationError("authorized_fields includes unsupported/global/destructive scope")

    mutation = manifest["mutation"]
    if not isinstance(mutation, Mapping) or not mutation:
        raise ValidationError("mutation must be a non-empty object")
    mutation_keys = frozenset(mutation.keys())
    if mutation_keys != authorized_set:
        raise ValidationError(
            "mutation keys must exactly equal authorized_fields; implicit scope is forbidden"
        )

    status = mutation.get("status")
    if status is not None:
        if not isinstance(status, str) or not status.strip():
            raise ValidationError("status must be a non-empty string")
        if status.strip().lower() in DISALLOWED_STATUSES:
            raise PolicyError("destructive/ephemeral WordPress status is forbidden")

    # Values must be JSON-serializable deterministically and finite.
    _canonical_bytes(mutation)

    actual_hash = canonical_package_hash(manifest)
    if actual_hash != claimed_hash:
        raise ValidationError("package_sha256 does not match canonical manifest bytes")

    return dict(manifest), actual_hash


def make_envelope(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Helper for package builders/tests; execution still fully revalidates."""
    manifest_copy = json.loads(_canonical_bytes(manifest).decode("utf-8"))
    return {
        "manifest": manifest_copy,
        "package_sha256": canonical_package_hash(manifest_copy),
    }


@dataclass(frozen=True)
class ExecutionReceipt:
    status: str
    package_id: str
    package_sha256: str
    target_kind: str
    target_id: int
    before_sha256: str
    after_sha256: str
    verified: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "package_id": self.package_id,
            "package_sha256": self.package_sha256,
            "target": {"kind": self.target_kind, "id": self.target_id},
            "before_sha256": self.before_sha256,
            "after_sha256": self.after_sha256,
            "verified": self.verified,
        }


class MemoryLedger:
    def __init__(self) -> None:
        self.records: dict[str, dict[str, Any]] = {}

    def get(self, package_id: str) -> Mapping[str, Any] | None:
        record = self.records.get(package_id)
        return dict(record) if record else None

    def put(self, package_id: str, record: Mapping[str, Any]) -> None:
        self.records[package_id] = dict(record)


class JsonLedger:
    """Small atomic reference ledger.

    Production integration may use a stronger datastore, but it must retain these semantics:
    one package_id -> one immutable package hash, written only after verified destination state.
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ReplayConflict("idempotency ledger is unreadable; refusing execution") from exc
        if not isinstance(value, dict):
            raise ReplayConflict("idempotency ledger is malformed; refusing execution")
        return value

    def get(self, package_id: str) -> Mapping[str, Any] | None:
        value = self._load().get(package_id)
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ReplayConflict("idempotency record is malformed")
        return value

    def put(self, package_id: str, record: Mapping[str, Any]) -> None:
        data = self._load()
        existing = data.get(package_id)
        if existing is not None and existing != dict(record):
            raise ReplayConflict("package_id already has a different verified record")
        data[package_id] = dict(record)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(
            prefix=self.path.name + ".", suffix=".tmp", dir=str(self.path.parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, self.path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)


class ContentPublishControl:
    def __init__(
        self,
        *,
        adapter: ResourceAdapter,
        ledger: Ledger,
        allowed_targets: Iterable[tuple[str, int]],
    ) -> None:
        targets = frozenset(allowed_targets)
        if not targets:
            raise PolicyError("external page/post allowlist must not be empty")
        for kind, resource_id in targets:
            if kind not in ALLOWED_KINDS or isinstance(resource_id, bool) or not isinstance(resource_id, int) or resource_id <= 0:
                raise PolicyError("external allowlist contains an invalid target")
        self.adapter = adapter
        self.ledger = ledger
        self.allowed_targets = targets

    def execute(self, envelope: Mapping[str, Any]) -> ExecutionReceipt:
        manifest, package_hash = validate_envelope(envelope)
        package_id = manifest["package_id"]
        kind = manifest["target"]["kind"]
        resource_id = manifest["target"]["id"]
        target = (kind, resource_id)

        if target not in self.allowed_targets:
            raise PolicyError("target is not present in the external execution allowlist")

        existing = self.ledger.get(package_id)
        if existing is not None:
            if existing.get("package_sha256") != package_hash:
                raise ReplayConflict("package_id was previously verified with different bytes")
            current = normalized_snapshot(self.adapter.read(kind, resource_id))
            current_hash = snapshot_hash(current)
            expected_after = existing.get("after_sha256")
            if current_hash != expected_after:
                raise ReplayConflict(
                    "verified replay destination has drifted; refusing to claim idempotent success"
                )
            return ExecutionReceipt(
                status="already_verified",
                package_id=package_id,
                package_sha256=package_hash,
                target_kind=kind,
                target_id=resource_id,
                before_sha256=str(existing["before_sha256"]),
                after_sha256=current_hash,
                verified=True,
            )

        before = normalized_snapshot(self.adapter.read(kind, resource_id))
        before_hash = snapshot_hash(before)
        if before_hash != manifest["expected_before_sha256"]:
            raise PreconditionError("destination precondition fingerprint does not match")

        mutation = dict(manifest["mutation"])
        expected_after = dict(before)
        expected_after.update(mutation)
        expected_after_hash = snapshot_hash(expected_after)

        write_started = False
        try:
            write_started = True
            self.adapter.write(kind, resource_id, mutation)
            observed_after = normalized_snapshot(self.adapter.read(kind, resource_id))
            if observed_after != expected_after:
                raise VerificationError(
                    "destination readback differs from exact expected post-state"
                )
        except Exception as exc:
            if write_started:
                self._rollback_or_raise(kind, resource_id, before, exc)
            if isinstance(exc, ContentPublishError):
                raise
            raise VerificationError("destination write failed and was rolled back") from exc

        record = {
            "package_sha256": package_hash,
            "before_sha256": before_hash,
            "after_sha256": expected_after_hash,
            "target": {"kind": kind, "id": resource_id},
            "qd_artifact_id": manifest["qd_artifact_id"],
            "qd_decision_id": manifest["qd_decision_id"],
        }
        # Ledger failure happens after a verified content write. Fail closed and restore the
        # content so a retry cannot become an untracked side effect.
        try:
            self.ledger.put(package_id, record)
        except Exception as exc:
            self._rollback_or_raise(kind, resource_id, before, exc)
            raise ReplayConflict("ledger commit failed; destination was restored") from exc

        return ExecutionReceipt(
            status="implemented_verified",
            package_id=package_id,
            package_sha256=package_hash,
            target_kind=kind,
            target_id=resource_id,
            before_sha256=before_hash,
            after_sha256=expected_after_hash,
            verified=True,
        )

    def _rollback_or_raise(
        self,
        kind: str,
        resource_id: int,
        before: Mapping[str, Any],
        original_error: Exception,
    ) -> None:
        try:
            self.adapter.restore(kind, resource_id, before)
            restored = normalized_snapshot(self.adapter.read(kind, resource_id))
        except Exception as rollback_error:
            raise CriticalRollbackFailure(
                "rollback could not complete; destination state is UNKNOWN and requires manual verification"
            ) from rollback_error
        if restored != dict(before):
            raise CriticalRollbackFailure(
                "rollback readback mismatch; destination state is UNKNOWN and requires manual verification"
            ) from original_error
