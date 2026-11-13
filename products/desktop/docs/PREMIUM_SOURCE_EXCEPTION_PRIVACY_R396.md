# R396 — Premium financial CSV / human-review JSONL private exception custody

**Scope:** GrantAudit Studio Pro and ProcureGuard Studio Pro, offline source-report parsing and hash-linked human-review journal replay. **DRAFT / QD + founder HARD HOLD.** Issue [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Parent: R395 draft PR #2305. No production, distribution, payment, auto-review, real customer data, or original-file changes.

## Defect and risk

The two premium apps share `fvs_suite.exception_review`. On a malformed report or journal, the previous code used `raise ValueError(...) from exc` in five exception translators: missing-file, UTF-8 decoding, CSV header quoting, CSV body quoting, and JSONL UTF-8/JSON parsing. That deliberately retains the original exception under `__cause__`, and the user-facing exception can be passed to logging/UI layers. A `UnicodeDecodeError.object` can hold **the entire financial source byte buffer** (bounded by existing 64 MiB report limit); a `JSONDecodeError.doc` can contain a private journal record.

A Linux Python prepatch minimal reproduction confirmed an invalid UTF-8 input with `PRIVATE-ACCOUNT-987` and an invalid JSON string containing `PRIVATE-SUPPLIER-987` were accessible on `ValueError.__cause__`. This demonstrates an in-process error-object exposure path, **not** an observed customer breach or proven external exfiltration.

## Change

- Translate all five failure categories **after** exiting the source exception handler, rather than using `from exc` or `from None` within the handler. This removes automatically retained `__cause__` and `__context__` references from translated error objects.
- Preserve existing generic messages, including bounded report physical row numbers and journal record indices; do not echo confidential report bytes or paths.
- Keep unrelated errors from `read_regular_bytes` as-is: its own preexisting `_redact_os_errors` decorator translates ordinary OS errors to a path-free ValueError. The `_read_file` catch is additional defense in depth for direct/mocked `FileNotFoundError` propagation.
- No effect on report SHA-256 binding, source-row provenance, Decimal handling, journal hash chain, timestamp validation, locking, or human-only decisions. No source/journal reformatting or mutation.

## Executed evidence and boundaries

- **Executed locally (Linux Python 3.13.5):** 16 isolated reconstructed boundary test cases PASS in normal mode and 16 PASS under `-OO -W error`, **32 focused executions total**. Includes invalid UTF-8, malformed CSV header/body, malformed JSON, invalid journal UTF-8, path errors, duplicate JSON key, and valid grants/procurement reports. These reconstructed tests are **not actual full-repository execution** or proof that the remote committed integration suite passed.
- **Committed full-checkout suite:** `products/desktop/tests/test_premium_source_error_privacy_r396.py`: 15 synthetic unittest methods for both premium products and nonmutation, error-chain absence, normal parsing, and duplicate-key enforcement. These are authored but **not executed locally** because a complete repository checkout and native Windows environment are unavailable.
- Added the 15-method suite to the independent `desktop-source-evidence-r385.yml` workflow in normal and `-OO` Python on Ubuntu and Windows.
- Pre-existing R395 CI failures occurred *before runner assignment/steps* (source #43375709102, desktop #43375709101). There is **no evidence of passing hosted CI** until GitHub Actions runner eligibility is restored.

## Rerun on the exact PR head

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_premium_source_error_privacy_r396.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_premium_source_error_privacy_r396.py
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_premium_review_utc_integration_r395.py
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_safety_smoke.py
```

**Limitations:** Removing chained low-level exceptions does **not** make traceback frame locals inaccessible to privileged in-process debuggers, does not add encryption-at-rest, and does not prevent an unrelated caller from handling the original raw data unsafely. Native Windows/Ubuntu full integration, licensed packaging, Defender checks, accessibility, premium access controls, QD and founder approval remain required.

## Next highest-impact step

Fix GitHub Actions runner allocation and execute the **exact R396 SHA** on both Ubuntu and native Windows, including 15 newly committed real-import integration tests, inherited R395 chronology suites, all six product/Decimal and provenance suites, AES-GCM, Ed25519 and SQLite. Inspect failed-check annotations, Actions billing/spending limits and hosted-runner eligibility if jobs again show no steps. Only after green evidence should release-candidate packaging, Defender scan, keyboard/screen-reader acceptance, and authenticated premium distribution be considered. No untested executable or unrestricted premium URL may be published.
