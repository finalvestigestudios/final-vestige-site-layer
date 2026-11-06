# EX2 — isolated WordPress/Assembler acceptance runner (2026-11-06)

**Status: IMPLEMENTED and LOCALLY UNIT-TESTED; WORDPRESS STAGING NOT EXECUTED; RELEASE HOLD.**  
**Source base:** PR #1300, exact base SHA \`b03ced998272a8dec5a70c5f6a48b31d54fe6599\`.  
**Runner first committed:** \`74d9f062fec436fd4d1188cb83fa2e96e9f84393\`; extended at \`e4b6e44a3fcb1bb1dbcf90e3114ad7c05490ece7\`.  
**Runner Git blob:** \`6edc8af89a7e4b34940377f22ee698f1b3fae87f\`.  
**Unchanged review Blueprint Git blob:** \`455c6cccbf8a00e6ecc4c2524775010d7ee1762c\` (PR #1294/#1300). Frozen PR #49 remains \`10495883299d53596992c26a8987f629b2904670\`; untouched.

## Why this is different from the earlier static/PHP tests

The predecessor proved that the PHP callback could run against a stub, and that the extracted source could render in Chromium; **neither established WordPress/Assembler integration**. This runner accepts only an explicitly isolated WordPress preview URL, requires the rendered \`.wp-site-blocks\` shell and the EX2 review marker, refuses the known production host and production's included \`wpcomstaging.com\` address, and checks the rendered seven-chapter page in **14 JS on/off browser scenarios across seven viewport sizes**. It also checks source-preserved records and the Focus CTA, live interaction families, no-JS visible historical evidence, reduced motion on the 390px scenarios, 200% CSS zoom, and the network response **body** for the Apollo and Franklin images, checking signatures, decode, dimensions, transferred length and SHA-256.

The optional axe-core bundle can run real browser WCAG scans when supplied. It **fails closed** if axe is absent. A separate, genuine Lighthouse report and accessible keyboard/manual test remain required before release; no synthetic measurements are called CWV.

## Actual evidence from this run

- **20/20 local negative and unit controls PASS.** Covers rejecting production and unauthorized staging URLs, accepting explicitly isolated URLs, rejecting non-HTTPS remote previews, rejecting fake image/HTML response bodies, decoding genuinely generated WebP/JPEG image bytes, and rejecting seven mutated invariants.
- **Real Chromium / exact-source static reproduction:** all 7 chapter anchors, 72/72 Margins records, 5 Focus destinations and 2 review images exist. **Admission correctly returns HOLD** because the static page has no WordPress shell. This is intentional proof that static screenshots cannot falsely pass the native gate.
- **Production-host negative control:** \`--url https://finalvestige.com/\` exits nonzero before a browser opens or a page is fetched.
- **No actual Playground / WordPress URL available here.** The container has PHP 8.4, Chromium and Python Playwright, but DNS/network package acquisition was unavailable; the connected WP account shows **only production site 256784396**.
- **Genuine 14-scenario native test, image response bytes, axe, Lighthouse, Safari, keyboard AT and host-specific WordPress.com/Jetpack behavior: NOT RUN.** No acceptance claim.

## Reproduce on an authorized isolated WordPress/Assembler import

First load the **unchanged** \`FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json\` into free WordPress Playground or isolated WordPress, verify its own \`FV_EX2_WORDPRESS_IMPORT_ADMISSION_PASS\` result and confirm the isolated URL. On a browser runner with Playwright, Pillow, Chromium, and an approved local copy of the official axe-core JavaScript bundle:

\`\`\`bash
python experience2/home-flagship/playground/verify_integrated_playground.py --selftest
python experience2/home-flagship/playground/verify_integrated_playground.py \
  --url 'http://127.0.0.1:8899/fv-ex2-review/' \
  --axe /path/to/official/axe.min.js \
  --output /tmp/fv-ex2-gated-browser
\`\`\`

For a remote **explicitly isolated and approved** HTTPS host, supply \`--authorized-host <exact-preview-host>\`. Never use production URL or the site's included WordPress.com address as a staging URL. Do not install on production. A Playgrounds/review environment is not WordPress.com's host and does not establish Jetpack email/confirmation or field CWV.

The runner **intentionally exits HOLD even after its browser checks pass** until independent Lighthouse/CWV, genuine WCAG 2.2 AA human/AT checks, and site-owner acceptance are separately gathered. Treat any successful unit-test or generated fixture screenshot as **TESTED LOCALLY**, never **LIVE** or **VERIFIED PURCHASE**.

## Editorial/rights and conversion boundary

Read-only WP media metadata on 2026-11-06 reported Apollo #473 = **78,346 source bytes** and Franklin #474 = **466,043 source bytes**. These are **metadata**; no actual HTTP byte transfers were possible here. The Apollo alt/caption attribute S67-19766 to NASA with no endorsement; this is not a verified comparison of the delivered image pixels against the catalog original. Franklin is credited as the Commons-marked public-domain **1869 reproduced scan**, not a museum image of the original physical note. NYPL #1258 is **not in the candidate** while reuse of its exact capture remains under review. Do not add third-party commercial claims or images.

**OFFER → STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER:** existing free 52-page Focus Fieldbook → evidence-rich homepage CTA → full candidate not yet qualified on native WordPress and image payloads not proven → execute independent staging/browser acceptance and confirm download/signup path (no test subscriber without approval) → local 20/20 admission self-tests plus explicit fail-closed static replay only; zero verified transactions → homepage engineering/Site QA; Claude retains attribution, subscriber and checkout work; Grok/Praxxis retain acquisition. No net revenue claim.

**No production CMS writes, no merges, no deployment, no tracking changes, no spending.** Issues #150 and #820; PR #158 Apollo work remains in its own lane.