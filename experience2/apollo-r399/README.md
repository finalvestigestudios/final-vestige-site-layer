# Apollo Experience 2.0 — R399 Final HTML Tag Custody (draft, HARD HOLD)

**Scope:** additive staging-only source under `experience2/apollo-r399/`; parent R398 draft PR #2698. This is a **default-disabled alternative** to R395/R396/R397/R398, not another loader to enable concurrently. No WordPress, production, plugin settings, social, email, analytics, affiliate, payment or other external writes. No merge without independent QD, founder signoff and exact-head CI.

## Actual implementation

WordPress's [`WP_Styles::do_item()`](https://developer.wordpress.org/reference/classes/wp_styles/do_item/) invokes [`style_loader_tag`](https://developer.wordpress.org/reference/hooks/style_loader_tag/) after it generates the stylesheet link HTML. R398 checked only `style_loader_src`; an HTML filter could therefore add an event handler, tracking attribute, alternate media or other markup while keeping the approved CSS URL unchanged. This is a **local contract gap**, not a demonstrated production compromise.

R399 registers a second `style_loader_tag` filter at `PHP_INT_MAX` and requires **exact** WordPress-core link HTML for the two reviewed Apollo handles: canonical HTTPS URL plus fixed version, `rel=stylesheet`, exact `id`, `media=all` for gallery and `media=screen` for mobile correction, no injected attributes or extra markup. Any mismatch returns an empty tag. Existing R398 prepaint, canonical sibling paths, SHA-256-pinned NASA ledger (all 10 fields of 6 records), CSS checksums, staging environment, opt-in flag, approved Atlas page and handle-collision protections remain.

**Important limitations:** This is deliberately strict and may block harmless future WordPress HTML serialization changes. Late equal-priority filters, output buffers, RTL/inline styles appended outside the filter, CDN rewrites and actual HTTP/CSP/stylesheet delivery remain unverified. Actual installed WordPress/Assembler acceptance is a release blocker. Source code alone is not proof of actual browser network safety.

## Executable source-controlled checks

- `php -l experience2/apollo-r399/staging-final-tag-guard.php`
- `php experience2/apollo-r399/qa/print_gate.php`
- `php experience2/apollo-r399/qa/enable_print_gate.php`
- `php experience2/apollo-r399/qa/reproduce_r398_gap.php`
- `php experience2/apollo-r399/qa/tag_fixture.php` (emits 16 positive/adversarial native PHP tag cases)
- `python experience2/apollo-r399/qa/browser.py` (actual Chromium `page.set_content`, 13 display contexts and PHP-to-DOM tag test)
- `python experience2/apollo-r399/qa/package.py` (fixed-timestamp SHA-256-evidenced ZIP)

The browser test covers 320/360/390/768/1024/1440/1920px, no-JS, keyboard, touch, reduced motion, forced colors, 400% root-font stress, source links, print and fixture LCP/CLS. These are **local fixture** observations, not genuine axe-core, native 400% page zoom, installed staging, hosted CWV, or independently confirmed WCAG compliance. Hosted CI status must be checked on exact PR HEAD; no automatic release.

## NASA source fidelity, rights and one visitor action

The six-record ledger distinguishes the [original 1967 Apollo 204 Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) (the original ignition source was not conclusively identified) from [NASA's February 14, 2018 post-fire flammability account](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) (102 deliberately induced later Command Module ignitions). No NASA imagery or logos, speculative geospatial pins or commercial offers are added. Research Desk draft #158 remains untouched and separately needs photo-usage/rights QA.

One context-relevant path: verified Grok-owned Apollo documentary → NASA-backed Evidence Gallery → [free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → **only after founder/Claude/merchant verification** an optional rights-cleared classroom evidence kit. No paid CTA on the gallery. This is a funnel hypothesis, not attributable traffic or sales.

| OFFER → STEP | BLOCKER | CHANGE / TEST | EVIDENCE | OWNER |
|---|---|---|---|---|
| Apollo educator kit → paid order | Sellable SKU/rights/checkout/delivery unverified | Withhold paid CTA | HOLD, no merchant proof | Founder / Claude |
| Grok Apollo video → landing | Published asset ID/approved UTM unverified | Align one actual video to one gallery URL only after Grok approval | UNKNOWN, not zero | Grok / Praxxis |
| Evidence Gallery → free investigation | R398 allowed HTML-tag rewrites outside URL guard | R399 exact final tag filter and adversarial PHP+Chromium test | LOCAL FIXTURE PASS; STAGING HOLD | Apollo QA / QD |
| Verified purchase → realized net revenue | Audited qualified-human sessions, confirmed orders, refunds/fees absent | Use Claude's existing approved measurement, 7/30-day cohorts | Net revenue/1,000 qualified human visits NOT COMPUTABLE | Claude / Commerce |

Cross-references: [Apollo #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Homepage PR #49 and Grok/Praxxis TASK-008 are not modified. No release, posting, spending or tracking action authorized.
