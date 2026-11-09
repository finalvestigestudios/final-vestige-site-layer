# R300 — Private exception-chain custody for atomic text evidence reports

**DRAFT / QD + founder HARD HOLD.** Tracks #73. No `main` changes, executable release, compliance approval, or unrestricted premium distribution.

## Verified defect

The shared `fvs_suite.atomic_text.publish_text` used `raise ... from None` **inside** handlers for filesystem and staging errors. That suppresses a normal traceback's context display, but **does not clear** `exception.__context__`. A caller or diagnostic collector walking the chain could recover private input/output paths, OS diagnostic strings, or nested customer data. The risk affects locally generated Policy Delta comparisons and premium grant evidence manifests, without altering their report content or financial decision logic.

## Implementation

- Translate `OSError` to a new allowlisted error **inside** the handler and raise it **after** the handler exits; retain normal `PermissionError`, `FileExistsError`, and errno behavior, with `EIO` fallback for unclassified errors.
- Defer sanitized non-OS errors raised by `mkstemp` and `fdopen` until their handlers have exited. Preserve `MemoryError`, `KeyboardInterrupt`, `SystemExit`, and descriptor cleanup.
- Keep the original 64 MiB UTF-8 byte limit, exclusive no-clobber publication, staged byte reread, fsync, source immutability, and deterministic report bytes. No network, AI, entitlement, pricing, CSV engine, or site changes.

## Reproducible focused evidence — ACTUALLY executed

Tested the exact committed `atomic_text.py` and 15-method regression file via **local Linux CPython 3.13.5**, with genuine temporary files and injected faults. For both Python modes:

```sh
cd products/desktop
python -W error -m unittest discover -s tests -p 'test_atomic_text_context_privacy_r300.py'
python -OO -W error -m unittest discover -s tests -p 'test_atomic_text_context_privacy_r300.py'
python -m py_compile fvs_suite/atomic_text.py tests/test_atomic_text_context_privacy_r300.py
```

- **15/15 normal PASS; 15/15 optimized PASS (30 focused executions).**
- An exact byte-for-byte copy of original R299 `atomic_text.py` (Git blob `5cfd400417d7f0d4231f6ad2f0fa0cd91323b693`) failed **11/15** of these same tests, reproducing the hidden exception-chain vulnerability. `from None` was demonstrably insufficient.
- Tested/committed Git blob identities: implementation `c7ae0dc9c04fa3eea0d4506f8ce7dae2de88b615`; tests `48bea6dcecf78fbf510c419c0e82ddab327e2aab`.
- Coverage includes lstat, mkstemp, fdopen, fsync, publication link/rename failures and collisions, nested secret exception causes, descriptor/staging cleanup, source byte identity, canonical errno, and interrupt/memory failure behavior.

**Not executed:** the complete repository test suite, native Windows x64 packaging, executable smoke/AV, manual accessibility, or protected premium distribution. No production release is authorized based on these focused Linux tests.

## CI and approval gates

The prior R299 GitHub Actions desktop run `42576462825` concluded failure with Ubuntu and Windows jobs showing no recorded steps or runner assignment. Owner must investigate GitHub Actions billing/spend restrictions, workflow permissions, and runner allocation. Then rerun the unchanged R300 SHA with full normal/`-OO` source suites, all six source and native Windows executable smokes, Defender, GUI/accessibility and entitlement tests. Independent QD review and founder authorization remain mandatory. No binaries or download links are published.

**Next highest-impact engineering step:** restore runner execution; execute the complete suite including R298/R299 integration tests, and acquire genuine Windows 11 x64 candidate acceptance evidence.
