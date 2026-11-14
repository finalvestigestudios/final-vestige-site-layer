# Apollo R359 — resolved block-template pre-head asset discovery

**Draft staging research only.** Stack on R358; do not merge, deploy, alter WordPress content/settings, modify frozen homepage PR #49 or Research Desk PR #158, or publish a Grok asset. Source-of-truth #150; commercial measurement gate #820.

## Defect, mechanism, boundaries

R358 detects Apollo shortcodes in **explicitly assigned custom templates**, but WordPress default block-theme `page`, `single`, `front-page`, and `index` templates can still contain Apollo shortcodes without their CSS/optional JS being enqueued. R359 does **not** reconstruct WordPress's hierarchy. Instead, its `template_include` observer reads the **already-resolved** canvas path, `$_wp_current_template_id` and `$_wp_current_template_content` established by WordPress core `locate_block_template()`. It validates the active theme and exact template record against `get_block_template()`; the `wp_enqueue_scripts` hook then uses the existing bounded R357 nested-reference scanner and exact seven-style/one-script full Atlas or two-style/no-script standalone post-fire note handles. WordPress deduplicates handles across R357/R358/R359. No text, archival media, geolocation, transaction, or attribution code is added.

The two underscore-prefixed WordPress globals are **internal implementation details**, not a public compatibility API. If the canvas is replaced, the globals are missing/stale, the active theme or record differs, or the scan is incomplete, the R359 discovery **fails closed for assets** rather than guessing. Reader content remains under native WordPress rendering. The adapter must be installed together with reviewed upstream R357 and R358 files; it is not a standalone WordPress plugin. Actual installed Assembler/WordPress behavior remains **UNVERIFIED**.

Official code reference: https://developer.wordpress.org/reference/functions/locate_block_template/ and https://developer.wordpress.org/reference/functions/get_block_template/.

## Reproducible tests

```
php -l experience2/apollo-r359/resolved-block-template-prehead.php
php experience2/apollo-r359/qa/wp_contract.php
python experience2/apollo-r359/qa/browser_gate.py
python experience2/apollo-r359/qa/build_evidence.py
```

The PHP suite is 31 simulated WordPress API scenarios (default block templates, nested parts, malicious/mismatched/stale records, global drift, missing references, conditional loading and deduplication). The independent Chromium Playwright fixture tests 320/390/768/1440/1920px, no-JS and JS, keyboard, touch, reduced motion, forced colors, 400% root font, source filters, named accessible links, print source annotations and local LCP/CLS observations. These are **not** installed-WordPress acceptance, axe-core, manual screen readers, Safari/Firefox, hosted CI or production CWV.

## Editorial and commercial boundaries

Apollo 204 Board's most probable initiator was an electrical arc; a definitive single ignition source was not established. The separately classified 2018 NASA retrospective documents 102 later flammability test ignitions; these are not 1967 Board findings. NASA source URLs do not grant commercial image/trademark/endorsement clearance. There are no invented Atlas pins or edges, no embedded NASA photos, and no purchase link.

One editorial pathway: Grok Apollo long-form asset (approved campaign tags only) → NASA Evidence Atlas → existing **free Apollo investigation** → separately reviewed paid educational product **only after** a live, rights-cleared, payable SKU and checkout are independently verified. Marketing ownership stays Grok; Praxxis handles independent creator QA; Apollo handles staged evidence UI and test evidence. Source attribution and 7/30-day net revenue per 1,000 qualified humans remain uncomputable without valid landing sessions, confirmed paid orders, fees/refunds and merchant records.

**Release HARD HOLD:** actual Assembler block-theme installation, genuine axe-core/independent screen readers, Firefox/WebKit, browser-enforced HTTP/CSP, hosted exact-HEAD CI, media-rights review, authenticated commerce, founder/QD authorization.
