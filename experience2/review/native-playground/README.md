# FV EX2 — Native WordPress Playground admission (2026-11-08)

**Isolation:** new review branch stacked on draft PR #1633 at exact parent `d8204c892e4b6fecefa4257ce75e747169c5deb9`. Frozen PR #49 (`10495883299d53596992c26a8987f629b2904670`) and production WordPress remain untouched. This is **not** a release recommendation.

## Why this exists

PR #1633 proves PHP HTTP responses under **WordPress-function stubs**. It does **not** prove native WordPress Core, active Assembler theme, real same-origin Focus navigation, accessible rendered content, or image delivery. The new script `verify_native_playground.py` defines an executable *native-WordPress-only* gate instead of treating another PHP stub pass as acceptance.

The runner requires all three distinct WordPress evidence sources before browser verification: (1) a real WordPress `/wp-json/` namespace response containing `wp/v2`; (2) actual REST record for `fv-ex2-review`; (3) the installed Assembler stylesheet. If missing, it fails closed and does not label a fixture as staging. It refuses production and external origins before requesting anything.

After admission it attempts **twelve real Chromium navigation and screenshot configurations** at 320×568, 360×640, 390×667, 768×1024, 1440×900 and 1920×1080, with JavaScript on/off and reduced-motion. It examines 7 chapters, 72 Margins, 5 isolated Focus links, no production Focus-link leak, viewport overflow, first-screen CTA (320×568), source HTML, and genuine same-origin Focus navigation with no email form or signup claim. No form is submitted. It can run local axe-core if the reviewer explicitly supplies the JS file; otherwise axe is **FAIL-CLOSED, not a skip-pass**.

**Known limits:** automated axe does not establish full WCAG 2.2 AA or manual screen-reader/touch/zoom quality. Image transfer-byte verification remains assigned to PR #1580; this runner does not certify it. Lighthouse/field CWV, live Jetpack, commercial attribution, image rights and full WordPress.com Atomic parity remain OPEN and are always marked as such. An isolated WordPress Playground has different cookies, Jetpack, CDN and routing from WordPress.com.

## Reproduce

1. Obtain the protected **PR #1626** private candidate ZIP (derived from PR #1620; sha256 `23c4073fb328ae6231380f68225af36645ab127b8df864e604aee1848f54b436`). Do not publish the bundle or include WordPress users, subscribers, secrets, production DB backups or commerce data.
2. On a separate authorized disposable WordPress Playground instance, load the ZIP using **New → Blueprint URL** for an appropriately private URL or the documented local Playground CLI `--blueprint=./private-bundle.zip`. The Blueprint installs pinned Assembler and creates **local** review pages only. No production install.
3. From an environment that can reach **that** isolated WordPress instance, run:
   `python experience2/review/native-playground/verify_native_playground.py --origin http://127.0.0.1:<PORT> --out evidence/`
   Optionally include `--axe-js /path/to/axe.min.js` (locally available copy; no subscription).
4. Run `python experience2/review/native-playground/verify_native_playground.py --self-test` for the strict-origin/false-WordPress negative controls. Use `report.json` and screenshots as source-linked review evidence; **do not use it to approve a release automatically**.

This environment has PHP 8.4 and Chromium but **no WordPress Core installation, no native Assembler install, no local Playground CLI cache, no Docker, and container DNS cannot retrieve wordpress.org**. The exact-source self-test yielded **13 passing isolation/negative controls**. A local refused TCP port correctly yielded missing Core REST, missing review-page REST and missing Assembler CSS; **native acceptance not run**.

## Conversion-first release contract

**Offer:** free 52-page Seven Day Focus Fieldbook. **Step:** evidence-first homepage → contextual Focus action → native Jetpack confirmation (production test by Claude) → verified paid conversion. **Blocker:** no real WordPress/Assembler staging admission; PHP stubs were not sufficient. **Change:** executable fail-closed native installation check and browser specification. **Pass/Fail:** 13 negative/security tests pass, real staging gate **BLOCKED**, commercial outcome **not measured**. **Owners:** interim homepage engineering for staging UI/QA; Claude for production Jetpack and attribution; Grok/Praxxis for acquisition. Commercial KPI *net revenue per 1,000 qualified human sessions* is uncomputable without verified session and settled-order data.

**Additional release holds:** NYPL map derivative item rights and actual media bytes, Apollo/Franklin source bytes and rights review, true WordPress Core/Assembler execution, axe and manual WCAG 2.2 AA, keyboard/no-JS/200% zoom/mobile, lab Lighthouse and field CWV, Focus false-success issue #1613, failed GitHub Actions and missing independent QD approval. Founder approval required for every production change; no new affiliate links, email campaigns, tracking, merges, or deployments.