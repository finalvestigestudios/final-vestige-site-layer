"""Operator-side SQLite reservation ledger for offline premium entitlement issuance.

This is NOT customer authorization, authenticated audit logging, or a server-side
purchase check. Keep one operator-controlled registry outside every Git worktree.
Reservations are never silently undone or reused, including after a failed
signing or write attempt. Investigate uncertain operations manually.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re
import sqlite3
import stat
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from registry_schema_guard import RegistrySchemaError, enforce_registry_schema
from registry_row_guard import RegistryRowError, enforce_registry_rows

PRODUCTS = frozenset({"grants", "procurement"})
IDENTIFIER = re.compile(r"^[A-Za-z0-9_-]{4,64}$")
MAX_LICENSE_BYTES = 8192


class RegistryError(ValueError):
    """The operator must resolve this registry or issuance problem manually."""


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _path_fingerprint(path: str | Path) -> str:
    # Never store a customer-identifying absolute fulfillment path in the DB.
    return hashlib.sha256(os.fsencode(os.path.abspath(path))).hexdigest()


class IssuanceRegistry:
    """Single-machine, fail-closed license ID reservation and issuance record.

    All operators must use the SAME protected local database. SQLite's unique
    index and BEGIN IMMEDIATE serialize concurrent issuer processes. A different
    database, copied database, or an administrator editing it is not protected.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        if not self.path.is_absolute() or self.path.suffix != ".sqlite3":
            raise RegistryError("Registry must be an absolute .sqlite3 path")
        parent = self.path.parent
        if not parent.is_dir() or parent.is_symlink():
            raise RegistryError("Registry requires an existing, non-symlink directory")
        if any((ancestor / ".git").exists() for ancestor in (parent, *parent.parents)):
            raise RegistryError("Registry must live outside Git worktrees")
        if os.name == "posix" and (parent.stat().st_mode & 0o077):
            raise RegistryError("Registry directory must be owner-only (0700)")

    def _check_file(self) -> None:
        if self.path.is_symlink():
            raise RegistryError("Registry must not be a symlink")
        flags = os.O_RDWR | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(self.path, flags | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            try:
                descriptor = os.open(self.path, flags)
            except OSError as exc:
                raise RegistryError("Cannot open protected registry") from exc
        except OSError as exc:
            raise RegistryError("Cannot create protected registry") from exc
        with os.fdopen(descriptor, "rb", closefd=True) as handle:
            metadata = os.fstat(handle.fileno())
            if not stat.S_ISREG(metadata.st_mode):
                raise RegistryError("Registry must be a regular file")
            if os.name == "posix" and (
                metadata.st_mode & 0o077 or metadata.st_uid != os.getuid()
            ):
                raise RegistryError("Registry file must be owned and readable only by operator")

    @contextmanager
    def _db(self):
        self._check_file()
        conn = None
        initialized = False
        setup_fault = False
        try:
            conn = sqlite3.connect(str(self.path), timeout=5, isolation_level=None)
            conn.execute("PRAGMA busy_timeout=5000")
            conn.execute("PRAGMA journal_mode=DELETE")
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("""CREATE TABLE IF NOT EXISTS issuance (
                license_id TEXT PRIMARY KEY,
                product TEXT NOT NULL CHECK(product IN ('grants','procurement')),
                kid TEXT NOT NULL,
                output_path_sha256 TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('reserved','issued')),
                license_sha256 TEXT,
                reserved_at TEXT NOT NULL,
                issued_at TEXT
            )""")
            initialized = True
        except sqlite3.Error:
            setup_fault = True
        finally:
            # SQLite connect can succeed and a subsequent PRAGMA/DDL can fail.
            # No partially configured connection may remain open on failure,
            # including KeyboardInterrupt/SystemExit paths.
            if not initialized and conn is not None:
                try:
                    conn.close()
                except sqlite3.Error:
                    pass
        # Raise only after the private SQLite fault has left the handler.
        # Chaining (even "from None") retains paths in __context__.
        if setup_fault:
            raise RegistryError("Cannot initialize protected registry")
        try:
            yield conn
        finally:
            conn.close()

    def reserve(self, *, license_id: str, product: str, kid: str,
                output: str | Path) -> None:
        """Durably reserve a globally unique ID before touching private keys.

        A failed subsequent issuance leaves a persistent reserved entry, and
        therefore cannot silently recycle a possibly issued license ID.
        """
        if not isinstance(license_id, str) or not IDENTIFIER.fullmatch(license_id):
            raise RegistryError("Invalid license ID")
        if not isinstance(kid, str) or not IDENTIFIER.fullmatch(kid):
            raise RegistryError("Invalid signing key ID")
        if product not in PRODUCTS:
            raise RegistryError("Unknown premium product")
        destination = Path(output)
        if not destination.is_absolute() or destination.suffix != ".fvslicense":
            raise RegistryError("Output must be an absolute .fvslicense path")
        if destination.exists() or destination.is_symlink():
            raise RegistryError("Entitlement output already exists; never overwrite")
        with self._db() as db:
            try:
                db.execute("BEGIN IMMEDIATE")
                try:
                    enforce_registry_schema(db)
                    enforce_registry_rows(db)
                except (RegistrySchemaError, RegistryRowError) as exc:
                    raise RegistryError("Unsafe registry schema or issuance records; investigate manually") from exc
                output_hash = _path_fingerprint(destination)
                if db.execute("SELECT 1 FROM issuance WHERE output_path_sha256=? LIMIT 1",
                              (output_hash,)).fetchone():
                    raise RegistryError("Entitlement destination already reserved; investigate manually")
                db.execute("""INSERT INTO issuance
                    (license_id, product, kid, output_path_sha256, state, reserved_at)
                    VALUES (?, ?, ?, ?, 'reserved', ?)""",
                           (license_id, product, kid, output_hash, _stamp()))
                db.execute("COMMIT")
            except sqlite3.IntegrityError as exc:
                db.execute("ROLLBACK")
                raise RegistryError("License ID already reserved or issued; do not reuse") from exc
            except sqlite3.Error as exc:
                db.execute("ROLLBACK")
                raise RegistryError("Could not durably reserve license ID") from exc

    def finalize(self, *, license_id: str, product: str, kid: str,
                 output: str | Path, expected_sha256: str) -> str:
        """Finalize only the exact signed bytes verified by the issuer.

        expected_sha256 is computed from the in-memory signed payload, not
        from another read of the destination path. Never reuse a reservation
        after a mismatch; a human must investigate.
        """
        if (not isinstance(expected_sha256, str)
                or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256)):
            raise RegistryError("Expected signed-payload SHA-256 must be canonical lowercase hex")
        destination = Path(output)
        if not destination.is_absolute() or destination.is_symlink():
            raise RegistryError("Issued file must be an absolute regular file")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(destination, flags)
            with os.fdopen(fd, "rb") as handle:
                metadata = os.fstat(handle.fileno())
                if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_LICENSE_BYTES:
                    raise RegistryError("Issued file is not a bounded regular file")
                content = handle.read(MAX_LICENSE_BYTES + 1)
        except OSError as exc:
            raise RegistryError("Cannot read issued entitlement for fingerprint") from exc
        if len(content) > MAX_LICENSE_BYTES or not content:
            raise RegistryError("Issued file is empty or exceeds size limit")
        digest = hashlib.sha256(content).hexdigest()
        if not hmac.compare_digest(digest, expected_sha256):
            raise RegistryError("Issued file differs from verified signed payload; reservation retained")
        with self._db() as db:
            try:
                db.execute("BEGIN IMMEDIATE")
                try:
                    enforce_registry_schema(db)
                    enforce_registry_rows(db)
                except (RegistrySchemaError, RegistryRowError) as exc:
                    raise RegistryError("Unsafe registry schema or issuance records; investigate manually") from exc
                finalized_at = _stamp()
                cursor = db.execute("""UPDATE issuance SET state='issued',
                    license_sha256=?, issued_at=? WHERE license_id=?
                    AND product=? AND kid=? AND output_path_sha256=?
                    AND state='reserved' AND license_sha256 IS NULL
                    AND reserved_at <= ?""",
                    (digest, finalized_at, license_id, product, kid,
                     _path_fingerprint(destination), finalized_at))
                if cursor.rowcount != 1:
                    db.execute("ROLLBACK")
                    raise RegistryError("No matching reserved issuance or unsafe clock; investigate manually")
                db.execute("COMMIT")
            except sqlite3.Error as exc:
                db.execute("ROLLBACK")
                raise RegistryError("Could not durably finalize issuance") from exc
        return digest
