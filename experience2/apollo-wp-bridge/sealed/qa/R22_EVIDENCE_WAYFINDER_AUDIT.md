# Apollo Experience 2.0 — R22 Evidence Wayfinder QA and editorial admission

**Date:** 2026-10-31 PT · **Release:** DRAFT / HOLD · **Owner:** separate Apollo component lane, Issue #150.

## Provenance & scope

- **Stack parent:** R21 PR #313, exact base `b0af560f0f64645fb9eff480257caf226ca9f0f6`.
- **Research Desk witness:** PR #158 (`250d7f05a4de037e73826dcf0cfaef0ec4c29383`); this PR is not edited or merged.
- **Apollo editorial source pinned:** `74375657f2cdaac0710f94c6de6c24534ee06858`.
- **Protected:** homepage PR #49, homepage lead branches, live WP and settings. No edits, installs or deployments.

## Implementation

Seven verified no-JavaScript native anchors connect **source concordance, chronology, typographic source gallery, independent Research Desk crosswalk, per-image NASA media-rights review, conservative Atlas admission, and seven editor-only SHA-256 research receipts**. Builder refuses inconsistent NASA source count, cleared-reuse claims, absent catalog-label hold, new coordinates/edges or export-count drift. The assembled private WordPress PHP adapter verifies the exact seven anchor targets and hash-seals `wayfinder.html` and `wayfinder.css` with a new response header. Read-only staging admission verifies the header, nav content, exact destinations and disclosed holds. No media reuse or speculated geo pins.

## Reproduced tests

- **131/131 Python + PHP simulated WordPress integration/security tests passed**, from `python -m unittest discover -s qa -p 'test_*.py' -q`.
- **7/7 real Chromium/Playwright Wayfinder responsive runs passed**, widths 320, 360, 390, 768, 1024, 1440, 1920 px. Seven real existing destination IDs unique; native keyboard/focus, touch native anchors, no JS (390 and 1920), reduced motion, 420px WordPress-like nested layout, source year filter 1967=3; no root horizontal overflow. Browser-derived CSS contrast minimum **6.63:1** across 32 text nodes per width. Native disclosures are in underlying casefile.
- Existing full responsive browser suite `qa/browser_exact.py`: 7/7 passes; Chromium AX-tree R16: 7/7; custody-receipts R21: 7/7; Atlas-admission R19: 7/7.
- **Synthetic**, in-memory Chromium LCP 156–384ms, synthetic CLS 0 at 7/7. Not hosted p75/production Core Web Vitals or certification.
- Standalone `php -l` passed. Exactly repeatable staging builds: `4c0b76e6868fd4526c1ca230c04c0321c5c2ee9bf38d7b77465dc94cf87329a7` SHA-256 (two identical runs).
- Strict `python qa/browser_exact.py --require-axe` failed **as expected**: no pinned verified axe-core JS bundle. Axe not executed, no WCAG certification.
- Screenshots SHA-256: r22-wayfinder-390.png:0383fcee6d23eb7cee4db0e97c0bc978c0ac8626b825c306b9cabc978d75334a, r22-wayfinder-1440.png:64480da69b201bc05dc320f615ff28bb97f7d4a6e4ca7c019532ad23f6718241.

## Reproduce

From `experience2/apollo-wp-bridge/sealed/` with PHP, Python and Chromium Playwright available:

```sh
python -m unittest discover -s qa -p 'test_*.py' -q
python qa/browser_wayfinder_r22.py
python qa/browser_exact.py
python qa/ax_tree_r16.py
python qa/browser_custody_receipts_r21.py
python qa/browser_atlas_admission_r19.py
python qa/browser_exact.py --require-axe  # intentionally fails closed without independently pinned axe
python build_sealed.py --out /tmp/r22-stage-a.zip
python build_sealed.py --out /tmp/r22-stage-b.zip
sha256sum /tmp/r22-stage-a.zip /tmp/r22-stage-b.zip
```

## Unresolved non-waivable gates

No actual WordPress installation/Assembler/Jetpack staging test; browser network navigation blocked by runtime administrator, so browser-enforced HTTP CSP/cookies untested. Axe-core strict gate RED (verified bundle absent), no actual Safari/VoiceOver/NVDA, no hosted CI/p75 LCP/CLS/INP or independent QD/founder review. Six individual NASA photographic reuse approvals missing; photo gallery remains **typographic source plates**, no embedded NASA images. PR #158 `NASA S67-19766` catalog-label inconsistency remains editorially unresolved. Atlas zero coordinates or inferred edges. **Do not merge, deploy, or write to WordPress.**

NASA official media guidance: https://www.nasa.gov/nasa-brand-center/images-and-media/
NASA original source example (1966 training): https://www.nasa.gov/image-detail/amf-s66-58038/
