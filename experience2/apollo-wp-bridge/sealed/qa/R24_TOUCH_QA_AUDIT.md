# Apollo Experience 2.0 — R24 touch-target accessibility repair / audit (2026-10-31)

**STAGING ONLY — DRAFT/HOLD.** Independent Apollo component development, based **only** on R23 PR #326 exact parent `4d345bb1f36f9e3318485825a664e81049ab3b9e`, original NASA casefile pin `74375657f2cdaac0710f94c6de6c24534ee06858`. Homepage PR #49, homepage lead branches, Research Desk PR #158, live WordPress, and main unchanged. No installations, merges, paid service, speculative pins or source-media embedding.

## Proven accessibility defect and repair

Baseline R23 Chromium accessibility measurement found **79 visible Apollo `<a>` elements shorter than 44 CSS pixels**, at both 390px and 1440px, spanning eight distinct classes (hero actions, source links, custody, claim ledger, ledger actions, gallery, Atlas and footer). This makes links difficult to tap even when semantic HTML and the AX tree are present. After a scoped CSS-only overlay the same 79 links are **at least 44px tall** (minimum width 88.67px) at all seven widths. Visible keyboard focus is reinforced; native no-JavaScript record filtering and disclosure are preserved. The canonical source files remain pinned and byte-identical.

Private plugin generates an immutable `touch-targets.css` using `qa/touch_targets_r24.py`, bound into the SHA-256-verified payload and exposed via `X-FV-EX2-Apollo-Touch-Targets-SHA256`. The read-only staging admission tests reject a missing CSS body or mutated digest, including adversarial new cases. No external requests, `url()`, embedded photos or scripts in overlay. CSS overlay should be reviewed for visual spacing by the founder, with real WP Assembler/Jetpack testing before release.

## QA and screenshot receipts

- Real **Chromium Playwright** rendered PHP via local PHP WordPress-function shim using `page.set_content`, **not browser HTTP navigation / true WordPress staging**.
- **7 / 7 widths** 320 / 360 / 390 / 768 / 1024 / 1440 / 1920: 79 of 79 target anchors at least 44px after repair, no horizontal root overflow, JS error count zero, focus outline checked, native keyboard/touch/no-JS and reduced motion checks passed; simulated 2x CSS zoom reflow passed (not OS zoom).
- Local synthetic LCP range **264–968ms** where observed, CLS **0** across all seven measured widths. They are **NOT field CWV**; real p75 CWV/INP unavailable.
- Python/PHP regression, exact Chromium baseline, Chromium AX tree and identity tests, reproducible package SHA will be reported with exact execution results in Issue #150; this audit does not assert unexecuted tests.
- **Axe-core:** NOT VERIFIED/NOT RUN. Strict certification gate remains blocked without independently version-and-SHA verified axe bundle.
- Six deterministic screenshot files, hashed here:
- `r24-screenshots/r24-hero-390.png` SHA-256 `ee236237a24d67a97ef84011bbe30ffa01db7a9dd8eccdf30d00521c522299f0`
- `r24-screenshots/r24-source-390.png` SHA-256 `ff97f532bedbedbda8571d48f891ec0dd57f9dfbc82dd2f3edd6c57d059babdf`
- `r24-screenshots/r24-gallery-390.png` SHA-256 `7eca872cf9fb9c254d0d03e5570e6d6acdf172d01e9a8ce7b76a633ac7590ebb`
- `r24-screenshots/r24-hero-1440.png` SHA-256 `b623df2e74b8d7ce78a71acff26c5407d81d3d47a300dc32552904c2aee86238`
- `r24-screenshots/r24-source-1440.png` SHA-256 `678bb8b22ec7bbf87186069aa3417d31297ff51c41a9baea77638776197d956f`
- `r24-screenshots/r24-gallery-1440.png` SHA-256 `03c119e23aa8e95d70883a539f2e473070213739ad58b97efb770f219180c1a3`

## Reproduce

```
cd experience2/apollo-wp-bridge/sealed
python -m unittest discover -s qa -p 'test_*.py' -q
python qa/browser_touch_targets_r24.py
python qa/browser_exact.py
python qa/ax_tree_r16.py
python qa/browser_catalog_identity_r23.py
python qa/browser_exact.py --require-axe  # MUST fail closed until verified axe distribution is provided
php -l fv-ex2-apollo-sealed-template.php
python build_sealed.py --out /tmp/r24a.zip
python build_sealed.py --out /tmp/r24b.zip
sha256sum /tmp/r24{a,b}.zip
```

## Still blocked

No actual installed WP Assembler/Jetpack staging; browser-origin HTTP navigation fails with `net::ERR_BLOCKED_BY_ADMINISTRATOR` even for loopback; no browser-enforced CSP/cookie run; no independently verified axe-core, Safari/VoiceOver/NVDA, hosted p75 CWV/INP, successful hosted CI, individual image-reuse/rights review, independently confirmed catalog accession `NASA S67-19766` for original linked photo, founder-selected artwork or independent QA. **DO NOT MERGE/DEPLOY.** Atlas remains zero admitted pins/edges.
