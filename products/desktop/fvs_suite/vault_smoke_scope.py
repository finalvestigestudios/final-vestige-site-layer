"""Packaged premium smoke: round-trip authenticated, product-scoped evidence.

Uses caller-provided *synthetic* premium report/journal, a temporary local root,
and the real vault restore function in packaged smoke. No telemetry, network,
real customer data, release approval, or payment/compliance decisions.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

_DENIED = "Encrypted evidence does not match this premium review product"
_PRODUCTS = ("grants", "procurement")


def _fail(invariant: str) -> None:
    # Never format financial source bytes, paths, passphrases or exceptions.
    raise RuntimeError("Packaged premium vault scope smoke failed: " + invariant)


def check_scoped_vault_roundtrip(
    archive: Path, root: Path, passphrase: str, product: str,
    report: Path, journal: Path, restore: Callable,
) -> Path:
    """Require a genuine matched restore and a fail-closed wrong-product one.

    The caller's root must be a private, synthetic TemporaryDirectory. The
    restored directory stays available for pre-existing case/journal checks.
    Reject unexpected files, altered ciphertext or substituted report bytes.
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
    if (restored / "exception-report.csv").read_bytes() != original_report:
        _fail("scoped report bytes changed")
    if (restored / "exception-report.review.jsonl").read_bytes() != original_journal:
        _fail("scoped journal bytes changed")
    if archive.read_bytes() != original_archive:
        _fail("scoped restore changed encrypted archive")

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
    if archive.read_bytes() != original_archive:
        _fail("cross-product restore changed encrypted archive")
    return restored
