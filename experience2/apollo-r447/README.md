# Apollo R447 — chronological media/source custody (staging ONLY)

**BUILT:** An isolated source-link gallery without copied NASA media, logos, imagery, advertising, Google Maps pins, event-photo misrepresentation, storage, trackers, checkout or PII. Designed to supplement (not replace) public Apollo Atlas and inherited Research Desk. Source records span October 1966 training; January 1967 preflight processing; January 27 accident Board findings; January 2017 hatch exhibit. This is a chronology of source *contexts*, not a reenactment of instrument timestamps.

**Historical boundaries:** Board finding 1: probable electrical arc, no conclusively identified single ignition source. NASA S66-58038 and S67-15717 catalog pages verified in source research November 17, 2026. Published FV Atlas links to KSC-20170124-PH_KLS01_0129, but the NASA image API could not be rechecked in the current tool: remain in `CATALOG_LINK_RECORDED_NOT_RECHECKED`, not silently verified. NASA's brand/advertising policy applies to any future commercial media reuse. No original imagery shipped.

## Files, shortcode and trust boundaries

`manifest.json` is SHA-256-pinned inside `gallery.php`; modifications must fail safe to an untagged free investigation link. `gallery.php` renders four chronologically ordered source records with native `<details>` and one free investigation next action. CSS and JS are scoped; JS reveals filter buttons only after initialization; all cards and source limitations are available no-JS. Staging shortcode: `[fv_apollo_rights_gallery]`, registered *only* if `wp_get_environment_type() === 'staging'` AND `FV_APOLLO_R447_ENABLE_STAGING === true`. Do not activate in production or assume plugin is installed. Dynamic/reusable block shortcode asset loading remains an acceptance test.

## Exact reproducibility

```sh
php -l gallery.php
python -m unittest discover -s qa -p test_contract.py -v
python qa/browser_qa.py
python qa/package_evidence.py
python qa/package_evidence.py
```

Chromium uses real browser controls but `page.set_content` (offline); navigation is blocked by policy. No axe-core and navigated LCP/CLS results should be claimed. Verifiable results are written to QA/browser_results.json and the deterministic ZIP, which is identical across repeated builds. Retain base exact branch and SHA, GitHub/CI, approved staging URLs, rights, independent QD and founder release gates.

## UX, business and ownership

**One intended pathway**: verified Grok long-form Apollo asset (none validated in R446) → public source-led Atlas → source/rights-aware evidence comparison → free investigation → optional founder-approved original classroom source analysis product when a rights-cleared payable SKU and fulfillment proof exist. The proposed paid educator product is a hypothesis, **not a sellable offer**. No CTA to the proposed product; no invented leads/orders or claimed revenue. Grok writes/posts; Praxxis reviews creators; Claude owns production engineering/measurement; Apollo/QD stages evidence; founder controls release.

Do not edit homepage #49, original Desk #158, TASK-008 or commerce/payment systems. Cross-reference GitHub Issue #150, #820 and business charter #818. R417 discrepancy, existing public Atlas editorial status ambiguity, rights review, approved staging, independent accessibility, CI and founder signoff remain HOLD.
