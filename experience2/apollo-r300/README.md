# Apollo Evidence Atlas R300 — repeated-instance accessible region names

**Staging only / HARD HOLD.** Parent [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150); commercial coordination [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) and charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Stack on the isolated Apollo R299 draft #2132. Do not touch the homepage PR #49, Research Desk PR #158, Grok/Praxxis content queues, or production WordPress.

## Defect and fix

The prior R297/R298 work gave distinct accessible names to five *inner* landmarks and to source `<details>` summaries when the shortcode renders twice. However, the **outer `<section aria-labelledby="...">` remained a named `region` with the same heading text** in every instance: “What the record establishes”. Unique `id` targets do not make the region names unique. In Chromium's actual accessibility tree, two such region nodes had indistinguishable accessible names.

R300 appends a visually hidden, naturally read instance marker to the referenced H2 itself. The unchanged visible H2 and section `aria-labelledby` continue to expose the appropriate accessible region name. If the CSS cannot load, the instance marker is **visible**, not dropped (fail open); no JavaScript is required. Historical records, original NASA links, source custody, eight source-limit statements, native chronology and the **single** existing free-investigation CTA are unchanged. No new sales callout or tracking code.

## Reproduce on source bytes

From `experience2/` with PHP 8+, Python 3, `playwright`, Chromium, and `pypdf` already installed:

```bash
php -l apollo-r281/apollo-source-experience.php
php apollo-r296/qa/compact_source_contract.php
php apollo-r295/qa/memo_custody_contract.php
python apollo-r296/qa/php_cache_gate.py
python apollo-r296/qa/compact_browser_contract.py
python apollo-r298/qa/disclosure_contract.py
python apollo-r299/qa/continue_cta_gate.py
python apollo-r300/qa/region_landmark_contract.py
python apollo-r300/build_archive.py
```

New R300 Playwright covers 320, 390, 768, 1440 and 1920 px with JS **off and on**, 2 shortcode instances each, native disclosure keyboard and deep-link focus, one relevant continuation each, unique IDs, no overflow, forced reduced motion, touch and a deliberately broken negative control removing the region suffixes. It reads `Accessibility.getFullAXTree`, not only DOM text. It checks the case without CSS. It emits five no-JS full-page screenshots, a normalized 13-page printable PDF preserving 70 link annotations, and an explicit JSON receipt. Offline Chromium PerformanceObserver LCP/CLS entries are diagnostics only; JS-disabled LCP may be null. These are **not** production or field performance scores. The normalized PDF and PNG bytes were reproduced across two consecutive runs with identical SHA-256 digests. Archive creation uses fixed ZIP entry timestamps and a sorted manifest; rebuild twice to verify identical archive hashes.

## Source/rights and conversion policy

Official original NASA Board narrative: https://www.nasa.gov/history/Apollo204/narr.html . NASA's 1967 source dates the initial oral authority January 27 and convening January 28. The later NASA safety summary uses different establishment wording; it is not independent eyewitness corroboration. NASA brand/advertising guidance: https://www.nasa.gov/nasa-brand-center/ and https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . Only source hyperlinks are used, without NASA media/insignia, commercial endorsement or speculative Atlas pins.

**OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER:** Apollo-focused rights-cleared educator dossier (prospective, *not sellable*) → Grok verified film to Apollo Atlas to free investigation, then only an approved relevant offer → no verified product/merchant acceptance or creator Apollo asset_id, and repeated AT region naming harms evidence navigation → R300 unique outer region names and fixture acceptance; separate commercial offer/audience/checkout validation before any paid CTA → 10/10 local browser contexts PASS; paid conversion and net revenue **NOT COMPUTABLE** → Apollo for component, Praxxis/Grok for creator URL/QA, Claude for production analytics and commerce checks, founder for product/launch approval.

No paid sales, commission, confirmed lead, qualified-human session cohort, or attributed creator conversion is inferred from local accessibility tests. Commercial KPI remains realized **net revenue / 1,000 qualified human sessions** with 7/30-day cohort and small-sample disclosure once actual settlement data exist.

## HARD HOLD — required before release

Real axe-core scan (not installed; registry DNS unavailable), independent VoiceOver/NVDA, WordPress/Assembler/synced-block acceptance, browser HTTP/CSP (the browser's localhost navigation has been administrator-blocked), exact-head hosted CI, p75 field LCP/CLS/INP, NASA rights/editorial review, founder approval. No WordPress writes, merges, deployment, ad/affiliate activation, email, Grok posts, paid services or homepage edits. The PDF is not tagged, and does not substitute for an accessible HTML experience.
