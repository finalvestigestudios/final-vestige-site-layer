# R189 — Gutenberg inline-fragment release-claim custody (DRAFT / HARD RELEASE HOLD)

Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked exclusively on R188 draft [PR #959](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/959) at immutable parent `81d0fb712b1730e8e4d9bd990b203b4e51883d42`, **not `main`**. No changes to the live WordPress site, financial data, premium distribution, binaries, or production.

## Reproduced failure and repair

R188's `check_visible_hold` searched **compact** text for URLs/extensions and **space-joined** text for release claims. Combining inline tag boundaries **inside** an important word and **after** its final token can defeat both searches. With source nodes `["Down", "load ", "now", "Pilot with us"]`, compact text is `DownloadnowPilotwithus` and spaced text is `Down load  now Pilot with us`; R188's release-claim pattern finds neither. A fragmented `.exe` followed immediately by a heading similarly disappears into a word or is split by a synthetic space.

R189 adds `catalog_fragment_custody_r189.py`, called from R188's actual `check_visible_hold` before the static six-app catalog can pass. It uses an internal separator between Python `HTMLParser.handle_data` nodes and finite, precompiled patterns that tolerate boundaries *within* important words while recognizing terminal boundaries without assuming whitespace. It fails closed on release/availability claims and executable/installer/archive suffixes, rejects an incoming separator character, native-container/type violations, >10,000 chunks, or >81,920 source characters. Diagnostic exceptions are generic, never quote hidden links or customer data. Existing R188 URL, markup, heading, card-status, contact-only, and human-review checks remain intact.

### Observed behavioral comparison

Four isolated reproduction inputs were checked against **the exact R188 URI, extension, release regexes** and the new R189 function in Python. R188 returned *not detected*; R189 returned *rejected* for each:

- `["Down","load ","now","Pilot with us"]`
- `["GrantAudit.e","x","e","Pilot with us"]`
- `["Re","leased","Pilot with us"]`
- `["Avail","able ","for ","down","load","Pilot with us"]`

These are synthetic privacy-safe examples and do not establish a live-site exploit.

## Artifacts

- `products/desktop/catalog_fragment_custody_r189.py`: bounded, deterministic, standard-library fragment detector.
- `products/desktop/catalog_visible_hold_r188.py`: actual scanner integration, preserving the original checks.
- `products/desktop/tests/test_catalog_fragment_custody_r189.py`: **43 focused unittest methods**, including eight actual HTMLParser node-boundary cases, benign-copy negative tests, Unicode sentinel, input shape, limits, and privacy checks.
- `products/desktop/tests/test_catalog_fragment_integration_r189.py`: **nine additional whole-catalog fixture integration tests** against the R186 six-app `verify_catalog` gate; committed for full-repository/hosted execution, **not claimed locally executed**.
- `.github/workflows/desktop-build.yml`: distinct R189 steps in both Ubuntu `source-tests` and Windows `windows-build`, each running both normal and `-OO` 52-test discovery plus the unchanged tracked Gutenberg draft preflight.
- `products/desktop/README.md`: maintenance note and release HOLD.

## Executed test evidence (local Linux, 2026-11-04)

Interpreter: **CPython 3.13.5**, Linux. These tests exercised the implemented R189 scanner source, independently of an installed full repository:

```sh
python -m unittest -q test_catalog_fragment_custody_r189.py
# Ran 43 tests; OK
python -OO -m unittest -q test_catalog_fragment_custody_r189.py
# Ran 43 tests; OK
python -m py_compile catalog_fragment_custody_r189.py test_catalog_fragment_custody_r189.py
# PASS
```

**86/86 focused method executions PASS**, with no skip or failure. The locally executed implementation's exact Git blob is `8dbc70208f04d99982da47caa0b442c24aa44699`, matching the branch's committed `catalog_fragment_custody_r189.py`. Local test source is logically equivalent to, but not asserted byte-identical with, the committed test module; **do not treat these results as full-repository, nine-test fixture integration, hosted Windows, or packaged-binary verification**.

## CI, quality and distribution hold

[Prior R188 hosted run #41863265338](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41863265338) completed **failure** on both `source-tests` and `windows-build` without any recorded job steps. Attempted job-log retrieval returned 404/BlobNotFound. This evidence **does not identify the root cause**; the repo owner must inspect the Actions run banner, billing/usage restrictions and runner provisioning. R189 CI should be reevaluated against its **unchanged head** once runners allocate.

**Unverified:** full 52-test suite on checked-out source, inherited tests (including outstanding Policy Delta real-file cases), actual Windows x64 builds and launch, physical Windows 11 screen-reader/keyboard/scale acceptance, Defender/EDR evaluation, code signing, and protected premium download entitlement. There are **no public download URLs** and no evidence of launch authorization.

**Next highest-impact action:** restore Actions runner allocation; run R189 and inherited test suites on both platforms; privately build/checksum/smoke-test all six x64 candidates; then get independent QD and founder sign-off before any site publication or public/premium download. All six applications remain **UNRELEASED / HARD HOLD**.
