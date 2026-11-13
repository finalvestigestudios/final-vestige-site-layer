# Apollo R326 — source-custody bridge and hostile-source release gate (STAGING ONLY)

**Release: HARD HOLD.** Independent of frozen homepage PR #49 and Research Desk PR #158. No runtime changes; this sprint adds a deterministic test that guards current Apollo EvidencePlate/SourceDrawer/ChronologyRail source/rights boundaries and flags a concrete source-classification ambiguity in the *actual* Research Desk PR #158 code. Nothing was installed or deployed.

## Exact source identity

- R325 PHP `91745c286b2f23fb8a93058afb58905a2756714e`; CSS `550e1dc6ac869ebbda1b371343a6cdd91f8608f4`; JS `f85617e5f12ba747908ac507261f69c377369de7`.
- PR #158 head `250d7f05a4de037e73826dcf0cfaef0ec4c29383`; `templates/ledger.html` Git blob `403d128c57b9bc82dac7c619651689070edef86c`. Six card kinds and their two source URLs were extracted via authenticated GitHub read on Nov 12, 2026, and frozen in `qa/pr158_custody_snapshot.json`. This is a *review snapshot*, not a sync with PR #158; re-review whenever its head moves.

## Owner-review finding (no PR #158 edits)

- Research Desk evidence 02 labels itself **PRIMARY REVIEW BOARD RECORD**, but its first `NASA archive record` goes to a NASA **image-detail/photo accession** `S67-15717`. The separate second link really is the Review Board report. The label/source relationship is ambiguous, **not** proof the historical oxygen claim is false.
- Research Desk evidence 03 labels **INSTRUMENT CHRONOLOGY**, but its first source link is image accession `S66-58038`; timing should be attributed to the Board report linked second, not the photo. This is an *editorial source-classification review requirement*, not a claim that the image is fake.
- The Apollo Atlas itself deliberately keeps textual investigation records separate from four unlicensed-for-promotion **link-only** NASA photo records. No speculative pins, implied NASA commercial endorsement, or invented purchase are allowed.

## Actual executed local gate

Run from repo root: `python experience2/apollo-r326/qa/source_custody_bridge.py` with Python Playwright + Chromium + PHP + Node available. It verifies Git blobs before running, renders the real PHP shortcode through the existing WordPress-function test stub, exercises 14 offline Chromium contexts (320–1920px, JavaScript on/off, touch and reduced motion), follows NASA source -> evidence -> free-investigation decision anchors and confirms focus continuity, checks 3 documentary citations, 4 contextual-only NASA photo records, no geo, one editorial CTA, correct image-rights and non-endorsement boundaries, no merchants. Five deliberately corrupted fixtures must fail: photo-as-report, photo-as-claim proof, merchant substitution, invented geographic pin, and rights misrepresentation. It writes JSON and two Chromium screenshots under `QA/`.

LCP/CLS are **offline fixture** observations only, with browser PerformanceObserver where JavaScript is available. Missing no-JS LCP entries are reported `null` rather than fabricated. These cannot establish production Core Web Vitals or actual campaign attribution.

## Gates still blocked

Genuine axe-core not installed or executed; no independent screen-reader/Safari/Firefox acceptance; native browser HTTP/CSP is administratively blocked; no installed WordPress/Assembler/CDN or hosted CI results at exact SHA; no authenticated Grok Apollo asset ID; no founder-approved payable/right-cleared Apollo product; no independently confirmed paid purchases, fees, refunds or qualified human sessions. PR #158 classification needs its own owner's editorial correction; do not edit PR #158 here. Founder approval still required for release.

## Conversion-first experiment (not authorized for live activation)

`Grok Apollo documentary (asset ID unverified)` → `Atlas with NASA document-class proof` → **one** existing free Apollo investigation CTA → `separately approved, actually payable educational evidence kit`. Hypothesis: accurately labeling photos versus Board findings increases trust and reduces mismatched expectations, *not* proven sales. Use first-party consented/approved instrumentation and merchant records to assess 7/30-day cohorts. Net realized revenue / 1,000 qualified human sessions is **not computable** at this stage; a CTA click or lead is not a paid order.
