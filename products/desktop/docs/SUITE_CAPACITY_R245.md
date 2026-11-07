# R245 — Bounded large desktop source suite (issue #73)

**DRAFT / QD + founder HARD HOLD.** Source-only CI/test-capacity repair, **not** verification, authorization or publication of six standalone Windows x64 executables.

## Problem / scope

At R244 the tests directory contains **283 Python files** (281 `test_*.py` modules). Three security-bounded checks were 256, so the complete repository gate fails even if GitHub Actions runner allocation is restored:

- `scripts/offline_source_gate.py`: `MAX_TEST_FILES = 256`, test inventory and parent summary validation.
- `scripts/unittest_provenance.py`: `MAX_TEST_MODULES = 256`, complete discovery guard.
- `scripts/source_smoke_gate.py`: `MAX_SOURCE_FILES = 256`, package traversal and source inventory.

## Change and acceptance

Increase **all three caps to 512**, preserving strict upper bounds; do **not** expand `MAX_TEST_CASES = 20000`, `MAX_SOURCE_BYTES = 16 MiB`, diagnostics, launcher list or release gates. Add `tests/test_suite_capacity_r245.py`: real 281-module unittest discovery, source-only private digests, 283-file test inventory, exact 512 acceptance/513 rejection, malformed/bool counts, symlink rejection, and mutation during six synthetic smokes. Add normal/`-OO -W error` prepackage jobs on both Ubuntu and Windows before the existing full R57 source gate.

## Actual evidence and limits

The 10-method new regression file was executed on Linux using an **isolated reconstruction** of the three affected gate surfaces, with simplified fingerprint and smoke helpers: **10/10 PASS normal**, **10/10 PASS optimized**; `py_compile` passed. **This is not complete repository integration.** Committed regression tests have not been executed against the full exact repository; full source suite, hosted CI, native Windows x64 EXEs, antivirus, accessibility, licensing and premium fulfillment are unverified.

## Next proof

With trusted checkout and runners:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_suite_capacity_r245.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_suite_capacity_r245.py' -v
PYTHONPATH=products/desktop python products/desktop/scripts/offline_source_gate.py
```

Inspect/restore GitHub Actions runner allocation (recent Ubuntu and Windows jobs failed with zero executed steps); rerun the unchanged R245 head on both platforms. Independently QD-review real native Windows 11 verification, hashes, malware scan, keyboard/NVDA/high-DPI accessibility and gated premium delivery. Do not publish binaries based on source tests. Offline financial privacy, Decimal-safe calculations, deterministic audit evidence and human-only compliance decisions are unchanged.
