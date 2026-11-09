# R306 — Recheck premium vault stage bytes before private publication

**Scope:** GrantAudit Studio Pro and ProcureGuard Studio Pro shared `fvs_suite.vault_publish` path; issue #73. **DRAFT / independent QD + founder HOLD.** Branch stacked on R305, not production `main`. No executable or download published.

## Specific reproducible defect

R305 verified encrypted evidence on its original open file descriptor, closed the descriptor, and checked that the private staged pathname still identified the same regular file and had the expected **length**. Another local actor could rewrite ciphertext **in place on the same inode, with the exact same byte length**, after the descriptor closed. Existing checks still passed, allowing wrong bytes to be published. This is not a cryptography/key derivation bug or a compliance judgment.

Negative controls ran the **three new in-place-mutation tests against the byte-identical R305 helper** (Git blob `ee806cd488bf1c17fce5a5001e47d9389b3f6f13`): **3 tests executed; 3 expected failures** (no error raised). Corrupting the first byte, final byte, and rewriting all bytes then resetting mtime were all published by the predecessor.

## Actual change

- After R305's identity/length check and **before** the no-clobber publish operation, reopen the private staged path read-only with `O_NOFOLLOW` when available, and `O_BINARY` on Windows.
- Validate file identity, regular-file type, single-link custody and size through `fstat`. Reread all ciphertext in bounded `_BLOCK` chunks using the R304 short-read-safe reader; compare to the **exact** original payload. Demand EOF.
- Recheck descriptor identity, size, mtime and ctime after reading; check the staged pathname against the same identity and observed times after closing the read-only descriptor.
- Preserve R305 cleanup ownership, R303 no-overwrite exclusive final publication, sanitized exception chains, interrupts, local-only bytes, and exact financial/approval behavior.

**Limits:** This is a second point-in-time check, **not** a race-free defense against a hostile same-user directory actor replacing or mutating the stage after the final check. Filesystem clock granularity and file identity semantics vary. It adds another full sequential ciphertext read (up to the existing 120 MiB bound). NTFS behavior and all full integration tests require native CI. There is still no crash-durable metadata guarantee, external account, telemetry, AI approval, or expanded premium access.

## Actually executed evidence — Linux CPython 3.13, synthetic ciphertext only

The isolated workspace contains the byte-identical R305 source plus this 37-line addition and the new test module.

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_stage_recheck_r306.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_stage_recheck_r306.py'
python -m py_compile products/desktop/fvs_suite/vault_publish.py products/desktop/tests/test_vault_stage_recheck_r306.py
```

- **17/17 PASS** normal, **17/17 PASS** `-OO` = **34/34 method executions**; compilation PASS.
- Tests cover first/last byte tampering, same-size rewrite with restored mtime, short reads, blank/multiblock data, size shifts, prepublication read/open/EOF failures, privacy-safe error contexts, flags, interrupts, source validation and exclusive no-overwrite.
- **3/3 negative controls fail as expected** against original R305 behavior.
- Exact committed Git blob IDs matching locally executed bytes: `vault_publish.py` **`cc5d5c9f51bb477ea504d3c178e2cb8674675fb9`**, `test_vault_stage_recheck_r306.py` **`2812ee3762543eaa4ead807901ff7ccbcf62763a`**.

**NOT executed:** inherited R298–R305 full integration tests, the full six-engine checkout regression suite, hosted Ubuntu/Windows CI, genuine Windows x64 EXE build, NTFS behavior, Microsoft Defender, binary SHA-256 provenance, keyboard/accessibility, secure premium delivery, or website publication. Do not conflate focused Linux passes with binary acceptance.

## Mandatory next gates

1. Owner: restore GitHub Actions runner scheduling (check billing/spend, workflow policy, runner allocation) and rerun unchanged R306 head on Ubuntu and Windows with `products/desktop/scripts/offline_source_gate.py` — including every inherited test.
2. Evaluate Windows file identity/reopen and no-clobber rename on genuine NTFS. Fail closed if platform incompatibility is found.
3. Private six-app Windows 11 x64 build/smoke, signed/unsigned identity and SHA-256, Defender, keyboard accessibility, premium authentication/license handoff and independent QD/founder review **before** any release.

**Release / merge state:** HARD HOLD. No public executables, premium URLs, WordPress updates, automatic approvals, or production branch changes authorized by this sprint.
