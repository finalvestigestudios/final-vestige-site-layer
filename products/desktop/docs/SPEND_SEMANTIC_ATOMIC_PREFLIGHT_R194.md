# R194 — SpendMap atomic semantic-validation boundary (DRAFT / RELEASE HOLD)

Issue: #73. Parent: R193 draft #990 at immutable `f7c60ffe966411843b6ff6064e0fd0099be933b4`. This branch changes **no production/CMS content or downloads**. All six Windows x64 applications remain unreleased.

## Reproduced failure

On exact R193 `products/desktop/fvs_suite/spend_input.py` blob `6f80964e315873673bb5e8443892c0497dced71e`, the helper `validated_spend_rows(...)` completed whole-collection **shape** validation but then yielded each semantically checked transaction as it went. For a valid row 2 followed by invalid money/date/vendor/Decimal data in row 3, the first `next(iterator)` returned row 2 before learning the source collection was invalid. A direct iterator consumer could write misleading partial evidence. **22 of the new 28 synthetic R194 tests failed** against unchanged R193 source.

## Change

Validate and buffer the **entire** set of parsed semantic tuples before the first `yield`. This adds a bounded output list (existing 200,000-row cap), retains physical source references, source order, exact native Decimal values, privacy-safe messages, category defaults, callback order and once-only callback execution. The original input remains untouched; previously frozen dict snapshots remain owned by the helper.

**Not claimed:** Callback side effects cannot be rolled back; converters must be trusted. This is not proof that caller-provided source SHA-256 matches a descriptor-verified file, and it does not establish compliance/fraud or payment approval.

## Reproducible local evidence (2026-11-04)

- Isolated copy of exact Git-source-matched `spend_input.py`, with new tests and R193 inherited test file; **not a full repository checkout**.
- CPython 3.13.5 Linux normal: **52/52 PASS** (R194 28; inherited R193 24).
- CPython 3.13.5 Linux optimized `-OO`: **52/52 PASS**. Total **104/104** local method executions, no skips/errors/failures.
- Python compilation: PASS.
- Maximum-size synthetic probe: **200,000 rows / 1.74 seconds**, Linux local run, peak process RSS approximately **254,220 KiB**, includes fixture allocation. Neither a memory ceiling guarantee nor native Windows performance proof.
- Original inherited R193 test source blob `bb76cc6d0da6dfe1cdb6ce3e5a3834761fe963ab` used unchanged.
- No customer data, network use, telemetry, binary artifacts, premium URL, or external service.

## CI and QD

The existing `.github/workflows/desktop-build.yml` includes **both** Ubuntu full normal/`-OO` source regression discovery and Windows pre-packaging full normal/`-OO` source regression discovery. The new `test_spend_semantic_atomic_r194.py` is automatically included without modifying the shared workflow. This is **CI configured, not hosted CI PASS**.

R193 [Actions #41912429843](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41912429843) completed with Ubuntu and Windows failure and `steps=null` for both; no runner test or EXE evidence. If R194 also fails before allocation, the **owner** needs to inspect GitHub Actions run error banner, billing/usage quota, permissions, and runner provisioning, then rerun its unchanged commit.

**Next high-impact step:** unblock both hosted runners; execute full inherited integration (especially outstanding Policy Delta real-file cases), then privately build, checksum, malware-scan and launch each of six Windows x64 candidates. Perform physical Windows 11 keyboard/screen-reader/scale validation; verify premium entitlement-gated delivery, independent QD review and founder release authorization. **No merge or publication until approvals.**

## Local focused commands

```bash
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_spend_semantic_atomic_r194.py'
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_spend_semantic_atomic_r194.py'
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_spend_collection_preflight_r193.py'
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_spend_collection_preflight_r193.py'
```
