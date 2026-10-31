# Apollo Experience 2.0 — R17 dual-witness provenance and container-responsive QA

**31 October 2026 · DRAFT/HOLD · Issue #150 · Stacked exclusively on R16 draft PR #281 at `a3ef8e66ddf4a7af5ee0f1dd42443f931dfdf77e`.** Canonical 12-file evidence source remains PR #215 `74375657f2cdaac0710f94c6de6c24534ee06858`. This changes no legacy Research Desk PR #158, homepage PR #49/lead branches, WP site, or existing source/custody evidence.

## Improvement and historical boundary

Six source-concordance cards now visually separate (1) the original casefile's **editorial contextual finding** grounded in the NASA Apollo 204 Review Board from (2) the original NASA catalog's **photograph description**. The cards are explicitly not direct Board quotations. Each record links separately to its chronology claim, original source drawer, original NASA photographic catalog and the official Board report, with a native, keyboard-accessible limitation disclosure. Link labels include source/claim IDs rather than repeating indistinguishable actions.

The JSON custody index now carries source-controlled `editorial_finding`, `photograph_depicts`, `board_report_url` and explicit `evidentiary_relationship=photo_does_not_independently_prove_board_finding`. Each is derived from the unchanged pinned records, not invented by the renderer. No source permissions or timeline/geo claims are elevated: **six photograph URLs are external NASA links; zero photograph bytes, zero speculative coordinates, zero invented map edges**. In particular 1966 training and 2017 memorial photographs remain distinct from 1967 event findings.

The record grid is capped at two columns. A container-size rule collapses the two witnesses within narrow cards and the card grid within narrow WordPress blocks, including a **420px editor block inside a 1920px viewport**. This addresses a real earlier reading-width defect: four ~320px cards per row would squeeze two text columns into ~130px each.

## Executed QA (offline, exact pinned inputs)

- **82/82 Python/PHP tests PASS** (78 previous plus 4 new R17 mutation/escaping/custody cases).
- **7/7 real Chromium Playwright widths PASS**, 320/360/390/768/1024/1440/1920; keyboard native radio navigation, touch, no JS, reduced motion, 200% synthetic zoom, source deep links, six source drawers and Atlas/trail filters. Test script: `qa/browser_exact.py`.
- **7/7 CDP accessibility-tree audits PASS**, now **186 named interactive nodes per baseline width**, with 20 links absent from the accessibility tree after filtering five hidden cards; independently assert no unnamed interactive elements or broken anchor IDs. This is **not axe-core or a WCAG certification**.
- **7/7 independent R17 browser checks PASS** for six distinct photo/Board witnesses, 24 uniquely directed provenance links, native limitation disclosures, CSS container reflow and screenshot digest receipts, plus a 420px WordPress-column / JavaScript-disabled negative case (`qa/browser_dual_witness_r17.py`).
- Local synthetic LCP (where observed): **140–320ms** across five widths; 1440/1920 emitted no LCP, not zeros. Local synthetic CLS: **0** in seven widths. These values are from Chromium `page.set_content()` with embedded CSS, **not** installed WordPress, hosted LCP/CLS, real-user CWV or Lighthouse.
- Private staging package rebuilt twice and matched byte for byte: SHA-256 **`6995710944257e26b8f66336ef443983c4b5a82df8b0544f336003088f22b238`**, embedded PHP SHA-256 **`be827784946c3266c205ff68af7c2ef0ae699222ffb4791fb287f5fe26aaf0bb`**. No public plugin asset URLs.
- `python qa/browser_exact.py --require-axe` still deliberately exits nonzero: no independently verified axe-core JS bundle and SHA supplied. No fake accessibility pass was asserted.

## Reproduce

```sh
cd experience2/apollo-wp-bridge/sealed
python -m unittest discover -s qa -p 'test_*.py' -q
python qa/browser_exact.py
python qa/ax_tree_r16.py
python qa/browser_dual_witness_r17.py
python build_sealed.py --out /tmp/apollo-r17-a.zip
python build_sealed.py --out /tmp/apollo-r17-b.zip
sha256sum /tmp/apollo-r17-{a,b}.zip
# FAIL-CLOSED pending independently verified axe bundle:
python qa/browser_exact.py --require-axe
```

## Remaining non-waivable release gates

Actual editor-authenticated WordPress staging installation/Assembler/Jetpack, browser-enforced HTTP CSP/cookie/iframe behavior (Chromium localhost and intercepted HTTPS navigation returned `ERR_BLOCKED_BY_ADMINISTRATOR`), verified axe-core execution, Safari/VoiceOver/NVDA, hosted CWV, QD and green exact-head CI, founder visual approval, and per-photograph NASA media-rights review if any images are proposed for reuse. **DRAFT / HOLD. No merge or deploy.**

NASA Board primary source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
NASA image/media guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/
