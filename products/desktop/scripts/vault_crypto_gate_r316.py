"""Fail-closed execution gate for authentic premium AES-GCM integration tests.

Runs source-controlled integration modules, not mock substitutes or packaged EXEs.
Emits only bounded counts and fixed messages; never prints client paths, fixture
contents, passwords, private tracebacks or test skip reasons. QD/founder HOLD.
"""
from __future__ import annotations

import contextlib
import hashlib
import os
import stat
from pathlib import Path
import re
import sys
import unittest

from scripts.source_only_test_loader_r318 import load_source_suite

# These are real complete-checkout integration cases, not isolated mocked helpers.
# Both premium product flows and authentication, rollback, publication and
# source-custody paths must execute, not merely be discovered or skipped.
REQUIRED = (
    ("test_evidence_vault_r8.py", (
        "EvidenceVaultR8Tests.test_sealed_grant_roundtrip_authenticated_and_no_plaintext_leak",
        "EvidenceVaultR8Tests.test_no_review_journal_still_seals_report_without_approval",
        "EvidenceVaultR8Tests.test_procurement_roundtrip",
        "EvidenceVaultR8Tests.test_wrong_passphrase_writes_nothing",
        "EvidenceVaultR8Tests.test_tamper_ciphertext_and_nonce_fail_without_files",
        "EvidenceVaultR8Tests.test_truncated_header_fails_closed",
        "EvidenceVaultR8Tests.test_wrong_format_and_weak_passphrase_rejected",
        "EvidenceVaultR8Tests.test_stale_report_with_existing_review_refused",
        "EvidenceVaultR8Tests.test_corrupt_journal_refused",
        "EvidenceVaultR8Tests.test_collision_preserves_prior_vault",
        "EvidenceVaultR8Tests.test_source_symlink_is_rejected",
        "EvidenceVaultR8Tests.test_decrypt_creates_distinct_folders_without_overwrite",
    )),
    ("test_vault_publication_integration_r303.py", (
        "PremiumVaultPublicationIntegrationR303.test_actual_sealed_ciphertext_published_and_sources_unchanged",
        "PremiumVaultPublicationIntegrationR303.test_fail_fsync_leaves_no_final_archive",
        "PremiumVaultPublicationIntegrationR303.test_final_name_is_not_visible_while_staging_fsync_runs",
    )),
    ("test_vault_restore_writer_integration_r310.py", (
        "VaultRestoreWriterIntegrationR310.test_genuine_encrypted_restore_for_both_premium_products",
        "VaultRestoreWriterIntegrationR310.test_fsync_failure_is_private_and_rolls_back_both_products",
        "VaultRestoreWriterIntegrationR310.test_folder_creation_failure_is_private_before_any_plaintext",
        "VaultRestoreWriterIntegrationR310.test_postwrite_digest_mismatch_keeps_no_restored_plaintext",
    )),
    ("test_vault_product_integration_r312.py", (
        "ProductScopeIntegrationR312.test_mismatched_archives_fail_before_plaintext_for_both_products",
        "ProductScopeIntegrationR312.test_matched_archives_restore_for_both_products",
        "ProductScopeIntegrationR312.test_invalid_scope_rejected_without_plaintext",
    )),
)
_FILENAME = re.compile(r"test_[a-z0-9_]{1,80}\.py\Z")
_METHOD = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,100}\.test_[a-z0-9_]{1,100}\Z")
_FIXED_ERROR = "Premium AES-GCM integration gate HOLD: required source tests did not execute cleanly"


class IntegrationHold(RuntimeError):
    """Fixed public error, with no chaining of private test failures."""


def _cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _cases(item)
        else:
            yield item


def _source_witness(source: Path) -> tuple[object, ...]:
    """Snapshot source bytes AND filesystem identity, without echoing paths.

    This detects source replacement between preflight and final execution,
    including byte-identical substitutions. It is not an OS-level lock and
    does not guarantee absence of transient races between observations.
    """
    if source.is_symlink():
        raise IntegrationHold(_FIXED_ERROR)
    before = source.lstat()
    if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= 128 * 1024:
        raise IntegrationHold(_FIXED_ERROR)
    data = source.read_bytes()
    after = source.lstat()
    fields = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size,
                        s.st_mtime_ns, s.st_ctime_ns)
    if fields(before) != fields(after) or len(data) != before.st_size:
        raise IntegrationHold(_FIXED_ERROR)
    return fields(after) + (hashlib.sha256(data).digest(),)


def execute_gate(directory: Path, *, targets=REQUIRED) -> dict[str, object]:
    """Preflight all modules; then run exact required tests with zero skips.

    ``targets`` injection is only for isolated regression tests. Production CLI
    always uses the frozen ``REQUIRED`` inventory. A PASS is a SOURCE test
    result and never proves Windows, Defender, signing or distribution.
    """
    try:
        directory = Path(directory)
        if not directory.is_dir() or directory.is_symlink():
            raise IntegrationHold(_FIXED_ERROR)
        if (type(targets) is not tuple or not 1 <= len(targets) <= 16):
            raise IntegrationHold(_FIXED_ERROR)
        seen = set()
        vetted = []
        for filename, methods in targets:
            if (type(filename) is not str or not _FILENAME.fullmatch(filename)
                    or filename in seen or type(methods) is not tuple
                    or not 1 <= len(methods) <= 50
                    or any(type(m) is not str or not _METHOD.fullmatch(m) for m in methods)
                    or len(set(methods)) != len(methods)):
                raise IntegrationHold(_FIXED_ERROR)
            seen.add(filename)
            source = directory / filename
            witness = _source_witness(source)
            vetted.append((filename, {filename[:-3] + "." + m for m in methods}, witness))

        observed = 0
        # Suppress Python-level prints from test import, execution and errors.
        # Never include unittest error strings or skip reasons in the result.
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                for filename, required, initial_witness in vetted:
                    source = directory / filename
                    if _source_witness(source) != initial_witness:
                        raise IntegrationHold(_FIXED_ERROR)
                    # Compile vetted SOURCE bytes, not Python's timestamp/size
                    # cache. A forged .pyc can otherwise pass with changed .py.
                    suite, loaded, loader_errors = load_source_suite(source)
                    if loaded is not sys.modules.get(filename[:-3]):
                        raise IntegrationHold(_FIXED_ERROR)
                    if (loaded is None or
                            Path(getattr(loaded, "__file__", "")).resolve() != source.resolve() or
                            _source_witness(source) != initial_witness):
                        raise IntegrationHold(_FIXED_ERROR)
                    identifiers = [case.id() for case in _cases(suite)]
                    if (loader_errors or len(identifiers) != len(set(identifiers))
                            or not required.issubset(set(identifiers))):
                        raise IntegrationHold(_FIXED_ERROR)
                    result = unittest.TestResult()
                    suite.run(result)
                    if (not result.wasSuccessful() or result.testsRun != len(identifiers)
                            or result.skipped or result.expectedFailures
                            or result.unexpectedSuccesses):
                        raise IntegrationHold(_FIXED_ERROR)
                    if _source_witness(source) != initial_witness:
                        raise IntegrationHold(_FIXED_ERROR)
                    observed += len(required)
                # Earlier modules must also remain unchanged while later ones run.
                for filename, _, initial_witness in vetted:
                    if _source_witness(directory / filename) != initial_witness:
                        raise IntegrationHold(_FIXED_ERROR)
        return {
            "schema": "fvs-premium-crypto-integration-r316-v1",
            "modules": len(vetted),
            "required_cases_executed": observed,
            "skipped": 0,
            "scope": "PYTHON_AES_GCM_INTEGRATION_ONLY_NOT_WINDOWS_EXECUTABLE",
            "released": False,
            "qd_approved": False,
            "premium_download_authorized": False,
        }
    except BaseException:
        # Swallow private test exceptions before raising outside the handler:
        # `raise ... from None` would still retain an inspectable __context__.
        pass
    raise IntegrationHold(_FIXED_ERROR)


def main() -> int:
    tests = Path(__file__).resolve().parents[1] / "tests"
    try:
        result = execute_gate(tests)
    except IntegrationHold:
        print("HOLD: premium AES-GCM integration coverage unavailable; no release approval", file=sys.stderr)
        return 1
    print(f"PASS: {result['required_cases_executed']} required genuine premium AES-GCM "
          "cases, zero skips; SOURCE ONLY, independent QD + founder HOLD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
