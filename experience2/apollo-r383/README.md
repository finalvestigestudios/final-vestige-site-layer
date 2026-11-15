# Apollo Experience 2.0 — R383 reusable-block Atlas CSS/JS custody

**DRAFT ONLY · SOURCE BUILT · LOCAL STUB/BROWSER QA · NOT INSTALLED ON WORDPRESS · NOT APPROVED FOR PRODUCTION**

The R381 curated document Atlas (`[fv_apollo_curated_atlas_r381]`, R382 navigation hardening) enqueues its stylesheet and optional filter script only when `has_shortcode()` detects the tag in the queried post's direct `post_content`. A published `core/block` reusable block can contain the Atlas shortcode while the parent post has only a block `ref`. In that case R381's direct-post enqueue condition is false, so its CSS/JS can be missing even though the Atlas HTML renders. This is a source-level integration gap, **not a verified installed WordPress malfunction**. R378–R380 cover a different shortcode, the R377 Research Desk; they do not resolve R381 Atlas loading.

## Isolated change

`reusable-atlas-assets.php` is an *optional staging-only, read-only companion* to R381/R382. It registers no shortcode, preserves the original R381 callback, and adds only `wp_enqueue_scripts` priority 2. It checks the existing R377 staging environment gate, the exact R381 shortcode owner, all six sealed R377 records, the R381 asset checksum verification, and the relevant queried singular post. Its bounded, side-effect-free block traversal follows only published native `core/block` references, rejects cyclic/foreign/draft/missing/malformed refs even if a valid Atlas tag appeared elsewhere, ignores code/preformatted examples, and caps graph depth at 7, blocks at 200, and total text at 1 MiB. It enqueues R381's existing CSS and JavaScript handles *at most once*, never sitewide. Dynamic unknown block engines, template parts and site-builder surfaces are intentionally out of scope and must remain staging blockers. If assets cannot be trusted, no additional historical claims or assets are loaded by this companion; existing semantic HTML/free investigation remains accessible.

**No new historical record, NASA photo, map pin, JavaScript tracking, commercial CTA, analytics script, merchant connection, WordPress write, homepage change, or Grok task alteration.** Do not install on a public host or treat this branch as release permission.

## Reproducible tests

From a complete repo checkout with R381, R382 and R377 dependencies:

```sh
php -l experience2/apollo-r383/reusable-atlas-assets.php
php experience2/apollo-r383/qa/php_contract.php
python experience2/apollo-r383/qa/browser.py
python experience2/apollo-r383/qa/package.py
python experience2/apollo-r383/qa/package.py # identical checksum required
```

- PHP API stubs: 24 scenarios, 68 assertions passed; deliberately not a real WordPress parser, block renderer or installed Assembler theme.
- Chromium: 10 local fixture contexts, 139 assertions passed, widths 320/390/768/1440/1920, keyboard, touch, no-JS, reduced motion, forced colors and 400% root-font stress (not native browser zoom). This confirms that the Atlas's existing JS/HTML contract remained operable; **it does not prove the PHP companion actually ran within WordPress**.
- Chromium local fixture LCP and CLS are observations, not field metrics or real hosted staging CWV. The bundled R382 specimen lacks the actual R381 print stylesheet, so print NASA citation restoration was **not verified against that fallback fixture**; `qa/browser.py` demands six print sources when running the true R381 PHP renderer.
- Actual installed WordPress/Assembler, real HTTP/CSP/stylesheet waterfall, genuine axe-core, independent screen readers, CI at exact PR head and qualified purchases: **NOT VERIFIED**. Treat as release blockers.

## Source and commercial custody

Canonical NASA Board report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ (specific ignition source not conclusively identified). NASA later engineering account: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ (102 *deliberate*, post-disaster Command Module boilerplate ignitions, December 1967–February 1968). NASA images/media guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/ — government content often usable for educational/editorial works, but third-party rights, logos, identifiable persons and commercial/endorsement uses require independent checks; linking source documents does not provide a blanket commercial media license.

One demand-validation pathway only: **Grok-approved, documented Apollo video asset** (published ID/UTM still unverified) → **source-backed Atlas** → **existing free Apollo investigation** https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ → **future founder-approved educator kit, only after an actual rights-cleared SKU and checkout are confirmed**. No claim of traffic, subscriber or sales uplift; no verified paid offer attached to this component.

| Offer → step | Blocker | Tested change / experiment | Evidence | Owner |
|---|---|---|---|---|
| Educator evidence kit → paid order | No verified payable rights-cleared SKU or checkout | Withhold purchase CTA; validate demand/rights first | NOT VERIFIED | Founder / Claude |
| Grok Apollo video → qualified landing | Published asset ID, UTMs, human sessions unverified | Preserve Grok's creator queue; no synthetic attribution | NOT VERIFIED | Grok / Praxxis |
| Atlas → free investigation | Missing CSS/JS possible when shortcode nested in `core/block` | Add sealed read-only pre-head asset guard | Local PHP 24/24 scenarios, Chromium 10/10 contexts; **not installed WP** | Apollo QA |
| Paid orders → net revenue | Merchant settlements, refunds, fees, qualified cohorts unavailable | Require verified 7/30-day source-to-order evidence | KPI NOT COMPUTABLE | Claude / Commerce |

No changes to frozen homepage PR #49, Research Desk PR #158, Grok/Praxxis TASK-008, or live WordPress. Issue #150 is the design/source QA tracker; #820 and #818 govern all commercial outcomes. Production HARD HOLD until founder/QD authorization and independent installed staging/CI acceptance.
