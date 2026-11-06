# R234 — exact-length custody for staged text evidence

**Status: DRAFT. Independent QD + founder HARD HOLD.** This source-only sprint stacks on R233 draft PR #1257. No changes to production main, WordPress, published downloads, premium artifacts or release approval.

## Why this is needed

The shared text-report publisher writes Policy Delta Desk change reports and GrantAudit Studio Pro evidence manifests. Before R234 it discarded the result of the staged binary stream write, then flushed, fsynced and published the file. A short write could therefore create a truncated audit document, while an interposed writer could report a full byte count but leave shorter or longer evidence on disk. An apparently successful report must not silently omit or add financial/policy evidence.

## Implementation contract

1. Validate the write result is a native integer **exactly equal** to the already-bounded UTF-8 byte length. Reject short, zero (for nonempty payloads), negative, inflated, None, bool and integer-subclass results.
2. Flush staging, then inspect the real staged file size with fstat before fsync and exclusive publication. Reject short or expanded physical file lengths even if a writer claims it accepted all bytes.
3. Any mismatch fails closed with an EIO error through the existing R233 fixed-text privacy boundary; close the stream and remove private staging. Never publish partial/expanded output and never overwrite a preexisting report.
4. Preserve success semantics: exact UTF-8/LF/CRLF, empty evidence, no BOM, the R231 64 MiB ceiling, R232 anonymous temporary names, existing exclusive destination publication, offline work, unchanged Decimal calculations and human review requirements.

This is a byte-count/length guard, **not** cryptographic content readback, a multi-file atomic transaction, directory fsync/power-loss guarantee, or proof against a compromised operating system.

## Reproducible focused testing (synthetic local fixtures)

- Linux CPython 3.13.5. Baseline copied exactly from R233 publisher Git blob **d0a3cd5238c55606418e861cb708827a6ae1d376**. The new 20-test R234 module against this unchanged baseline produced **17 failures** (actual silent-publication gaps); three tests still passed.
- Fixed publisher Git blob **81297ee0f3c101880872fb241f2aeabf43837812** and new test module blob **221666fcb649e2eabcca4ad4fc5d16cbaf2c25f0** match locally executed files.
- New R234 tests: **20/20 PASS** normal, **20/20 PASS** optimized -OO.
- Exact SHA-matched inherited committed R28 publisher tests (blob 30f8c2dc63760b9ec16150c5460b5a93176bbea6): **12/12 PASS** normal and -OO.
- Exact SHA-matched inherited committed R233 privacy tests (blob f34025755a4899792d2d9dcab150b7d8e25dc18b): **12/12 PASS** normal and -OO.
- **88/88 local test-method executions PASS** with warning-as-error; compilation PASS. R231/R232 and the complete engine/repository suite were not locally executed. Synthetic file-like fault injection does not replace NTFS/Win11 acceptance.

Ubuntu and Windows CI source steps include the R234 20-case test module in both normal and optimized modes before packaging; these steps are configured, **not verified executed**. Previous R233 Actions [#42222461459](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42222461459) failed before any step: Ubuntu and Windows jobs both had runner_id 0 and steps []. Check R234 CI independently.

## Next release gate

Restore hosted runner provisioning/account or workflow permissions and rerun the exact R234 head. Execute the **complete inherited six-app regression suite**, then privately build and test six true Windows x64 executables on Win11. Verify file integrity, SHA256, malware/Defender, 100/200/400% scaling and accessibility, no telemetry, offline processing, and entitlement-gated Pro delivery. Obtain independent QD review and explicit founder release authorization before merging or publishing. **All six apps remain unreleased.**
