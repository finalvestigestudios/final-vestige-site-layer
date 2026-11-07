# Apollo Experience 2.0 — R199 source/limitation accessibility (DRAFT; NOT LIVE)

**Parent:** R198 draft PR #1474 at `bff83305dd71913105c8008115d657869dffd11a`. Scope is limited to `experience2/apollo-r199/`; homepage PR #49 and Research Desk PR #158 are unchanged.

## Defect and fix

R198 introduced four identical accessible names, “Read NASA technical source,” in its evidence-to-source crosswalk, despite an earlier sprint making eight disclosures individually identifiable. This makes assistive-technology link lists ambiguous. R199 uses four distinct, visible source link names, assigns each an `aria-describedby` relationship to the corresponding evidence limitation, and highlights the relevant claim card on keyboard focus. It explicitly warns that the four links open the **same complete NASA Apollo 204 Review Board report**, not section-specific deep links. The correction is native HTML/CSS and needs no JavaScript.

Unchanged: four chronology milestones, four technical findings, eight source disclosures, archival gallery with editorial source links, print-source index, optional campaign handling, fail-open fallback and the one free **Read original investigation** CTA. The NASA Review Board is a technical record; S67-21294 documents post-fire damage, not ignition; NASA's advertising/astronaut-likeness restrictions are distinct from research citation. No speculative map pins, scripts, media, new commerce, tracking or publishing.

## Reproducible local execution (full inherited pipeline required)

```sh
python -I experience2/apollo-r199/build_r199.py
php -l experience2/apollo-r199/dist/fv-ex2-apollo-r199.php
python -I experience2/apollo-r199/qa/gate_r199.py /tmp/apollo-r199-A
python -I experience2/apollo-r199/qa/gate_r199.py /tmp/apollo-r199-B
sha256sum /tmp/apollo-r199-A/*.png /tmp/apollo-r199-B/*.png
```

Requires Python 3, BeautifulSoup, Playwright and Chromium at `/usr/bin/chromium`. The script runs actual generated shortcode PHP using a **simulated WordPress-function harness**, then uses real Chromium Accessibility CDP and Playwright's DOM/touch/keyboard and screenshot APIs. Test results generated November 7, 2026: **2 independent passes × 12 contexts**, 320–1920px; **48 source focus/description pairs each run**, eight adversarial mutations rejected, **12/12 identical screenshot hashes**. No horizontal overflow. Offline fixture LCP 76–172ms for contexts with LCP entries and CLS 0. They are *not* field Web Vitals. The `dist/` assets are generated and not committed; their SHA-256 digests are in the manifest.

**Source custody:** R199's committed builder and QA script were compared byte-for-byte against locally executed code via their Git blob IDs. The inherited R198 *local source archive* was functionally equivalent to but not byte-identical with the R198 GitHub builder, so full exact-parent-GitHub-HEAD checkout acceptance remains open. Do not imply exact-HEAD pipeline CI passed.

## Release and conversion hold

**Not tested:** installed WordPress/Assembler, real browser URL navigation (localhost, `file:` and `data:` navigation blocked by browser policy), actual CDN/CSP/cache, genuine axe-core, NVDA/VoiceOver, actual zoom, qualified human visitors, or checkout. These require independent staging QA and founder authorization; zero production changes were made.

Flagship audience: historically curious educators/viewers from Grok long-form Apollo content; only after a real Grok `asset_id` and approved URL are confirmed. Current path: Grok asset → source-focused Atlas → **free original investigation** → proposed educator dossier purchase **only when an independently verified, rights-cleared sellable SKU and checkout exist**. This dossier is not a verified offer; no paid CTA is enabled. Grok owns scripts/posts and IDs; Praxxis owns creator QA; Claude owns production WP/analytics; founder approves release. No verified qualified-human denominator, leads, paid orders, refunds/fees or net revenue; 7/30-day net revenue per 1,000 qualified human sessions is **NOT COMPUTABLE**. Coordination #150, #820, charter #818 and unchanged TASK-008 Drive documents.

**STAGING HOLD. DO NOT MERGE OR DEPLOY.**
