# Labs R304 — short-read-tolerant premium vault byte verification (DRAFT / HOLD)

**Scope:** encrypted local evidence publication shared by GrantAudit Studio Pro and ProcureGuard Studio Pro; issue #73. This feature branch is stacked on the immutable R303 commit `53be1ece7ef433e65ef4057fcd91d3c155cd737b`, not on production `main`. Independent QD review and founder approval remain mandatory.

## Problem and fix

R303's fsynced, private staging verifier called `os.read(fd, block_size)` once and treated any shorter-than-requested read as a corruption error. POSIX and Windows read APIs may return fewer bytes than requested **without** indicating a damaged file. A valid short read consequently rejected an otherwise intact encrypted archive. The failure was safe (nothing published), but degraded reliability and could prevent backups in environments that expose short reads.

R304 adds bounded `_read_exact(fd, count)` verification. It accumulates bytes from successive reads until the expected verification block is complete; an early EOF, non-native `bytes` result, overlong result, underlying OS failure, or content mismatch remains fatal and must prevent final-name publication. Verification still runs **before** `fsync`, no-overwrite link/rename, and staging cleanup. A bounded block limits transient read memory. The content format, AES-256-GCM, Scrypt, source SHA-256, audit journal, Decimal money, privacy/no telemetry, and manual review policy are unchanged.

## Actually executed local evidence

Environment: isolated Linux CPython **3.13.5**, not native Windows. The two files tested are byte-identical to their committed GitHub blobs:
- `fvs_suite/vault_publish.py` — Git blob `f23c530a25a4f580f15e48964e60d43d9a27373d`
- `tests/test_vault_short_read_r304.py` — Git blob `2a4e272c1f2a7ba75f1403018f4d99068bd142ba`

Run from `products/desktop`:

```sh
python -W error -m unittest discover -s tests -p 'test_vault_short_read_r304.py'
python -OO -W error -m unittest discover -s tests -p 'test_vault_short_read_r304.py'
python -m py_compile fvs_suite/vault_publish.py tests/test_vault_short_read_r304.py
```

**15/15 PASS** standard; **15/15 PASS** optimized; **30/30 total focused test executions**; compilation PASS. Coverage run (15 methods, branch tracing) reported **85%** coverage for `fvs_suite/vault_publish.py`; this is *not* complete repository test coverage. Synthetic cases include genuine filesystem reads across 256 KiB boundaries, 1/7/8191-byte short reads, early EOF, forged types, overlong data, ciphertext tampering, OS error-chain path privacy, interrupt cleanup, destination preservation, exclusive collision handling, fsync-before-publication, and byte-exact output. A locally reconstructed R303-style one-shot reader was used as a negative control: it rejected an intact 1-byte-per-call read, while R304 succeeded.

## Unverified release gates and next step

- **NOT RUN:** all inherited repository regressions including unexecuted R298–R303 integration cases; hosted Ubuntu/Windows tests; true Windows 11 x64 executable acceptance.
- **NOT VERIFIED:** Microsoft Defender/EDR scanning, 46-observation physical accessibility review, signing, SHA-256 executable release inventory, or authenticated premium download/licensing.
- No premium artifacts or download links are public. No production site changes or QD bypass are authorized.

**Next highest-impact step:** Resolve GitHub Actions runner non-execution, rerun unchanged R304 commit on both Ubuntu and Windows, run the full normal and `-OO` desktop suite and R298–R304 integration tests, then perform private native Windows 11 x64 tests and separate QD/founder approval before any executable distribution.
