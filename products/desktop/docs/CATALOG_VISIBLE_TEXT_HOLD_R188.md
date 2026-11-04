# R188 — fail-closed visible-text release/privacy hold (DRAFT; NO PUBLICATION)

Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on R187 draft PR #953 (exact base SHA `953b18848bc4472280caebad7ee2f2430b91f7d3`), never on `main`. All six Windows x64 products remain **UNRELEASED**.

## Concrete defect reproduced

R186 checks approved HTML anchors, product labels and Gutenberg structure, but ordinary allowed `<p>` text could still include a **raw premium EXE URL**, a relative installer path or a misleading `AVAILABLE NOW` notice while retaining all six correct development labels. Bare text is not an `<a href>` attribute; the existing R186 link allowlist did not inspect it. Such source could enter a public CMS review by mistake.

## R188 changes

- New `catalog_visible_hold_r188.py` checks **decoded visible HTMLParser data nodes** after structural parse and before approval of the static draft. It rejects URL schemes (including plain-text HTTPS, file/S3/GS), `www.`, common desktop installer/archive extensions and explicit premature release claims, as well as format-control characters such as zero-width spaces, bidi controls, U+2028/U+2029 and unpaired surrogates. It rejects untrusted input container/text subclass types. Diagnostics never echo URLs, tokens or original draft text.
- `catalog_preflight_r186.py` invokes the new guard and preserves its generic `CatalogPreflightError`; pre-release/owner decisions remain HARD HOLD. The sole legitimate **contact anchor** is still separately validated by the existing R186 allowlist.
- Real HTML parser integration exposed a second bypass in the first R188 implementation: concatenating adjacent data nodes produced `.msixPilot` or `Download nowPilot`, hiding an extension/claim at a tag boundary. Fixed by inspecting both concatenated and boundary-separated node representations. Added regression tests.
- Source-draft preflight is required on **Ubuntu and Windows**, with 43 standalone guard methods + 10 integration methods under both normal Python and `-OO`, followed by actual tracked catalog preflight. On PowerShell, each command is checked for a nonzero exit code before continuing.

## Executed reproducible local evidence — 2026-11-04

Environment: isolated Linux Python **3.13.5**, source files manually reconstructed then confirmed to match exact GitHub Git-blob IDs; no private customer files, no installed external dependencies and no network access. Test command from `products/desktop`:

```sh
PYTHONPATH=.:tests python -m unittest discover -s tests -p 'test_catalog_visible*188.py' -q
PYTHONPATH=.:tests python -OO -m unittest discover -s tests -p 'test_catalog_visible*188.py' -q
python catalog_preflight_r186.py site/software-catalog.gutenberg.html
python -OO catalog_preflight_r186.py site/software-catalog.gutenberg.html
python -m py_compile catalog_preflight_r186.py catalog_visible_hold_r188.py tests/test_catalog_visible*188.py
```

- **53/53 tests PASS normal**, **53/53 PASS optimized**, **106/106 executions**, no skips or failures. These include 43 helper and 10 actual R186 parser integration cases, including true rejection of bare premium URL and malformed release-claim variants.
- **Unchanged tracked six-card Gutenberg catalog:** preflight PASS normal and optimized; result explicitly `PASS_STATIC_DRAFT_ONLY`, **not** a live publication or executable verification.
- Python compilation PASS.
- Evidence source custody, Git-blob SHA1 values:
  - Integrated R186 gate `a64c109026742ce07d2e1debdb02ea67d43b82ef`
  - R188 guard `1f5a001cf9401416faab19351fd7f79f73b7a7e0`
  - R188 43-method guard tests `962d2d21c5228b537ad8c66d998ac8eb8bd6d249`
  - R188 10-method parser integration `4799541790698c8a6ccbca432c558f75384dbeb7`
  - Unchanged six-card source draft `6ab8fc98223330caae28a9964f36ee8a0c9ce6af`
  - Dual-runner workflow `9d485320c93077f51ab71fc911bedbc9f384c577`

**Limitations:** This validates only a tracked source draft, not WordPress-rendered text, CSS visibility, browser accessibility, binary security, real entitlement controls or any release approval. Heuristic checks do not guarantee detection of every encoding/obfuscation scheme, and must never be treated as a substitute for independent review. The full inherited repository suite, physical Win11 screen reader/manual accessibility, six x64 builds, Defender/EDR, signing, premium gated downloads and live link readback are unverified. No production branch or CMS mutations.

## Release gates and next highest-impact work

1. GitHub Actions R187 [run #41853705574](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41853705574) previously failed on both jobs before step execution, leaving native Windows validation blocked. Inspect repository Actions execution banner, billing/usage limits, runner permissions and allocation; restore runners. R188's fresh exact-head run must execute both jobs before claiming hosted evidence.
2. Execute the full inherited suite, especially **14 pending Policy Delta real-file integrations**; build privately and smoke-test six Windows x64 candidates with checksums and source/identity custody.
3. Verify physical Windows 11 accessibility, Defender/EDR, signing and protected premium distribution; obtain independent QD review and explicit founder approval before any merge or publication. **No binaries or premium links published.**
