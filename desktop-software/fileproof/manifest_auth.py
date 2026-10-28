"""FileProof manifest authentication and no-overwrite persistence.

This protects an *existing* manifest against undetected editing when the verifier
knows the passphrase. It does not encrypt content, authenticate the person who
originally created it, or protect against deletion or rollback of whole files.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
from pathlib import Path

AUTH_FIELD = "authentication"
AUTH_SCHEME = "pbkdf2-hmac-sha256-v1"
KDF_ITERATIONS = 600_000
MIN_PASSPHRASE_LENGTH = 12
MAX_MANIFEST_BYTES = 64 * 1024 * 1024


def _canonical_bytes(value: dict) -> bytes:
    """Return deterministic UTF-8 bytes for every covered manifest property."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _mac(manifest: dict, passphrase: str, salt: bytes) -> str:
    base = {key: value for key, value in manifest.items() if key != AUTH_FIELD}
    key = hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"),
                              salt, KDF_ITERATIONS, dklen=32)
    return hmac.new(key, _canonical_bytes(base), hashlib.sha256).hexdigest()


def authenticate_manifest(manifest: dict, passphrase: str) -> dict:
    """Add an optional passphrase-derived MAC, never a plaintext secret."""
    if not isinstance(manifest, dict) or AUTH_FIELD in manifest:
        raise ValueError("A manifest can only be authenticated once.")
    if not isinstance(passphrase, str) or len(passphrase) < MIN_PASSPHRASE_LENGTH:
        raise ValueError("Use a passphrase with at least 12 characters.")
    salt = secrets.token_bytes(16)
    signed = dict(manifest)
    signed[AUTH_FIELD] = {
        "scheme": AUTH_SCHEME,
        "iterations": KDF_ITERATIONS,
        "salt": salt.hex(),
        "tag": _mac(manifest, passphrase, salt),
    }
    return signed


def verify_authentication(manifest: dict, passphrase: str | None) -> bool:
    """Return True only on a valid MAC, otherwise reject rather than downgrade.

    The caller MUST supply a passphrase whenever it expects authentication:
    an attacker can otherwise delete the authentication field entirely.
    """
    if not isinstance(manifest, dict):
        raise ValueError("Malformed manifest.")
    authentication = manifest.get(AUTH_FIELD)
    if authentication is None:
        if passphrase is not None:
            raise ValueError("Manifest is unauthenticated; refusing passphrase downgrade.")
        return False
    if not isinstance(authentication, dict) or set(authentication) != {
        "scheme", "iterations", "salt", "tag"
    }:
        raise ValueError("Malformed manifest authentication metadata.")
    if (authentication["scheme"] != AUTH_SCHEME or
        type(authentication["iterations"]) is not int or
        authentication["iterations"] != KDF_ITERATIONS or
        not isinstance(authentication["salt"], str) or
        re.fullmatch(r"[0-9a-f]{32}", authentication["salt"]) is None or
        not isinstance(authentication["tag"], str) or
        re.fullmatch(r"[0-9a-f]{64}", authentication["tag"]) is None):
        raise ValueError("Unsupported or malformed authentication metadata.")
    if not isinstance(passphrase, str) or not passphrase:
        raise ValueError("This manifest requires a passphrase.")
    actual = _mac(manifest, passphrase, bytes.fromhex(authentication["salt"]))
    if not hmac.compare_digest(actual, authentication["tag"]):
        raise ValueError("Manifest authentication failed: incorrect passphrase or altered manifest.")
    return True


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    values: dict = {}
    for key, value in pairs:
        if key in values:
            raise ValueError("Duplicate JSON key in manifest: " + key)
        values[key] = value
    return values


def _reject_nonfinite(value: str) -> object:
    raise ValueError("Non-finite JSON value in manifest: " + value)


def load_manifest(path: Path) -> dict:
    if path.stat().st_size > MAX_MANIFEST_BYTES:
        raise ValueError("Manifest exceeds the 64 MiB verification limit.")
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream, object_pairs_hook=_reject_duplicate_keys,
                          parse_constant=_reject_nonfinite)
    if not isinstance(value, dict):
        raise ValueError("Manifest must be a JSON object.")
    return value


def save_new_manifest(destination: Path, manifest: dict) -> None:
    """Publish only a complete file, using atomic hard-link (no overwrite).

    The destination and temporary file must reside on the same filesystem.
    On filesystems without hard-link support, fail closed rather than replace
    an existing path or leave a partially written manifest.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("Refusing to overwrite an existing manifest.")
    temp = destination.with_name(destination.name + "." + secrets.token_hex(12) + ".tmp")
    try:
        with temp.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(manifest, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        # Unlike os.replace (and os.rename on POSIX), link() never overwrites.
        os.link(temp, destination)
    finally:
        temp.unlink(missing_ok=True)


def read_passphrase_file(path: str | None) -> str | None:
    if path is None:
        return None
    secret_path = Path(path)
    if secret_path.stat().st_size > 16 * 1024:
        raise ValueError("Passphrase file exceeds 16 KiB.")
    secret = secret_path.read_text(encoding="utf-8").rstrip("\r\n")
    if not secret:
        raise ValueError("Passphrase file is empty.")
    return secret
