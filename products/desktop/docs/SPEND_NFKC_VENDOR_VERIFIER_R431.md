# R431 — independently verify NFKC-safe SpendMap original vendor evidence

**Issue:** #73 · **Product:** SpendMap Lite (free Windows x64, source-only draft) · **Release:** HOLD / QD and founder approval required. This change neither releases a binary nor proves complete Windows behavior.

## Fixed producer/verifier disagreement

The R430 verifier independently reconstructs the source-bound `source_vendor_labels` field, but its spreadsheet prefix check handled only ASCII `= + @ -`. The existing **production** exporter applies a second check, `has_unescaped_formula_prefix`, for the first meaningful character's NFKC-compatible operators. For an original vendor label starting `＋` (U+FF0B fullwidth plus), `＝` (U+FF1D), `＠` (U+FF20), `﹢` (U+FE62), `﹦` (U+FE66) or `﹣` (U+FE63), the producer writes a literal leading apostrophe to prevent CSV formula evaluation while the pre-fix independent verifier expected no apostrophe. **Result:** a valid, safely exported financial report could be rejected. This is an implementation-contract defect, not an observed customer exploit.

## Implemented

- `fvs_suite/spend_label_verify.py`: add a standalone, independently coded first-meaningful-character NFKC formula-prefix check. It handles native ASCII minus-decimal exceptions while requiring a CSV-protective apostrophe for compatibility forms. Keep the verifier independent of the generator, `engine`, the publisher, network modules and premium entitlements.
- `tests/test_spend_compatibility_formula_r431.py`: 20 new direct unit methods with fullwidth/small/superscript compatibility operators, ordinary negative decimals, already-escaped quotes, visible ASCII boundary whitespace, NBSP, literal source escape ambiguity, cross-bucket consistency, 33-label digest/truncation, and an independent comparison against the *unchanged real publisher prefix predicate*.
- `tests/test_spend_compatibility_integration_r431.py`: six committed, **not yet executed**, full-engine source/export/verifier methods. The final case confirms missing protective apostrophes are rejected.
- `.github/workflows/desktop-source-evidence-r385.yml`: run R431 direct and real-engine tests on **Ubuntu 24.04 and Windows latest**, normal and optimized Python, alongside inherited R430 suites.

**Unchanged:** source SHA-256 identity, Decimal financial amounts, 64 MiB input cap, bounded review preview, distinct vendor matching, canonical row citations, premium licensing, local-only handling, human compliance review and site/QD publication safeguards. The leading apostrophe is CSV presentation defense, *not* a change to original vendor identity.

## Evidence collected locally (2026-11-14)

Local isolated Linux Python 3.13 validated GitHub-matched source blobs and synthetic strings:

| Test scope | Normal Python | `-OO -W error` | Scope |
|---|---:|---:|---|
| R431 newly committed unit suite, 20 methods | 20 PASS | 20 PASS | Actual new verifier + unchanged real prefix guard |
| R430 inherited unit suite, 20 methods | 20 PASS | 20 PASS | Actual updated verifier |
| **Total** | **40 PASS** | **40 PASS** | **80 local test executions** |

Git object/source custody: modified verifier blob `dc23927b85ef88eb139eef1329d327460e70515a`; unchanged publisher guard blob `79e49395947db9bf5f2ea26a323243c73968a1b1`; R431 unit test blob `fe4aa7948e0547ffef0e70c90e08b2c549fc2af6`; inherited R430 unit test blob `44c12f2fa80ec80ed34084c2e506fff8eeadda87`. These match the locally executed Git hashes. Controlled pre-fix run of the new unit suite failed with 19 assertion/subtest failures; patched run passed. Source, unit tests and integration test compiled.

**Limitations:** These 80 executions are isolated source verification, not all six engines, not the six full-engine integrations, not native Windows testing and not a real EXE release gate. The full-engine tests require the private repository checkout and hosted/local compatible environment.

## Release blockers / next high-impact action

At R430 exact head, source CI run #43619492693 and desktop-build run #43619492604 ended in failure: four jobs showed **zero recorded steps and no assigned runner**. This prevents acceptance testing, with GitHub account billing/spend limits, hosted-runner eligibility or Actions policy still unconfirmed. Inspect those controls without changing billing automatically, restore runner execution, then run exact-head R431 and inherited suites and review all six new integration outcomes. Next independently validate six genuine Windows x64 EXEs, SHA-256, Defender scan, keyboard/screen-reader paths and protected premium distribution.

**Hard release hold:** `release_authorized=false`. Draft stacked on R430, not production `main`. No binaries, downloads, site publication, merges, financial uploads, licenses or user-data transmission. QD independent review and explicit founder approval are required before release.
