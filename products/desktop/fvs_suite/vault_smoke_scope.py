"""Packaged premium smoke: round-trip authenticated, product-scoped evidence.

Uses caller-provided *synthetic* premium report/journal, a temporary local root,
and the real vault restore function in packaged smoke. No telemetry, network,
real customer data, release approval, or payment/compliance decisions.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Callable

_DENIED = "Encrypted evidence does not match this premium review product"
_PRODUCTS = ("grants", "procurement")
_MEMBERS = frozenset((
    "exception-report.csv", "exception-report.review.jsonl",
    "sealed-evidence-manifest.json",
))
_MANIFEST_KEYS = frozenset((
    "schema", "product", "sealed_utc", "report_filename", "report_sha256",
    "journal_filename", "journal_sha256", "journal_present", "review_event_count",
))


def _fail(invariant: str) -> None:
    # Never format financial source bytes, paths, passphrases or exceptions.
    raise RuntimeError("Packaged premium vault scope smoke failed: " + invariant)


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate manifest field")
        result[key] = value
    return result


def _witness(paths: tuple[Path, ...]) -> tuple[tuple[int, ...], ...]:
    """Record pathname custody across denial; never expose pathnames in errors.

    lstat refuses to follow a swapped symlink. Metadata complements exact
    content checks: replacing a file with byte-identical contents is not an
    acceptable product-isolation smoke result. This is not a race-free lock.
    """
    return tuple((info.st_dev, info.st_ino, info.st_mode, info.st_size,
                  info.st_mtime_ns, info.st_ctime_ns)
                 for info in (path.lstat() for path in paths))


def _verify_restored_bundle(restored: Path, product: str, report: Path,
                            journal: Path, original_report: bytes,
                            original_journal: bytes) -> bytes:
    """Fail if any synthetic restored member is absent, substituted or altered."""
    children = list(restored.iterdir())
    if len(children) != len(_MEMBERS) or {p.name for p in children} != _MEMBERS:
        _fail("restored member inventory")
    if any(p.is_symlink() or not p.is_file() for p in children):
        _fail("restored member type")
    if (restored / "exception-report.csv").read_bytes() != original_report:
        _fail("scoped report bytes changed")
    if (restored / "exception-report.review.jsonl").read_bytes() != original_journal:
        _fail("scoped journal bytes changed")
    try:
        raw_manifest = (restored / "sealed-evidence-manifest.json").read_bytes()
        manifest = json.loads(raw_manifest.decode("utf-8"), object_pairs_hook=_unique_pairs)
    except (UnicodeError, ValueError, TypeError):
        _fail("invalid restored manifest")
    if not isinstance(manifest, dict) or set(manifest) != _MANIFEST_KEYS:
        _fail("restored manifest schema")
    if (type(manifest["schema"]) is not int or manifest["schema"] != 1
            or manifest["product"] != product
            or manifest["report_filename"] != report.name
            or manifest["journal_filename"] != journal.name
            or manifest["report_sha256"] != hashlib.sha256(original_report).hexdigest()
            or manifest["journal_sha256"] != hashlib.sha256(original_journal).hexdigest()
            or manifest["journal_present"] is not True
            or type(manifest["review_event_count"]) is not int
            or manifest["review_event_count"] < 1
            or type(manifest["sealed_utc"]) is not str
            or not manifest["sealed_utc"]):
        _fail("restored manifest evidence mismatch")
    return raw_manifest


def check_scoped_vault_roundtrip(
    archive: Path, root: Path, passphrase: str, product: str,
    report: Path, journal: Path, restore: Callable,
) -> Path:
    """Require matched authenticated restore plus fail-closed wrong-product one.

    The caller's root must be a private, synthetic TemporaryDirectory. The
    restored directory stays available for pre-existing case/journal checks.
    A denial must not alter previously restored evidence or source fixtures.
    This tests product isolation of the packaged code path, **not entitlement**.
    """
    if type(product) is not str or product not in _PRODUCTS:
        _fail("invalid smoke product")
    if not root.is_dir() or root.is_symlink():
        _fail("invalid synthetic root")
    before = {p.name for p in root.iterdir()}
    original_archive = archive.read_bytes()
    original_report = report.read_bytes()
    original_journal = journal.read_bytes()

    restored = restore(archive, root, passphrase, expected_product=product)
    if (not isinstance(restored, Path) or restored.parent != root
            or restored.name in before or not restored.is_dir() or restored.is_symlink()):
        _fail("scoped restore destination")
    if {p.name for p in root.iterdir()} != before | {restored.name}:
        _fail("scoped restore created unexpected contents")
    initial_manifest = _verify_restored_bundle(restored, product, report, journal,
                                                original_report, original_journal)
    if archive.read_bytes() != original_archive:
        _fail("scoped restore changed encrypted archive")
    if report.read_bytes() != original_report or journal.read_bytes() != original_journal:
        _fail("scoped restore changed source evidence")

    # The denial must leave every already-present bundle member, source and
    # destination directory intact. A byte-for-byte replacement is still a
    # custody violation even when report hashes and manifest fields match.
    witnessed = (root, restored, archive, report, journal) + tuple(
        restored / name for name in sorted(_MEMBERS))
    custody_before = _witness(witnessed)

    # Wrong-scope request uses a known-valid archive and the SAME passphrase:
    # failures due to a bad password, corrupt file or missing fixture cannot
    # masquerade as the required product-bound denial.
    opposite = "procurement" if product == "grants" else "grants"
    try:
        restore(archive, root, passphrase, expected_product=opposite)
    except ValueError as exc:
        if str(exc) != _DENIED:
            _fail("wrong-product denial reason")
    else:
        _fail("cross-product restore accepted")
    if {p.name for p in root.iterdir()} != before | {restored.name}:
        _fail("cross-product restore left plaintext")
    later_manifest = _verify_restored_bundle(restored, product, report, journal,
                                              original_report, original_journal)
    if later_manifest != initial_manifest:
        _fail("cross-product restore changed manifest bytes")
    if _witness(witnessed) != custody_before:
        _fail("cross-product restore changed filesystem identity")
    if archive.read_bytes() != original_archive:
        _fail("cross-product restore changed encrypted archive")
    if report.read_bytes() != original_report or journal.read_bytes() != original_journal:
        _fail("cross-product restore changed source evidence")
    return restored
