# Apollo R277 — staging WordPress bridge for editorial source custody

**DRAFT · UNMERGED · HARD HOLD · NOT PRODUCTION.** Independent Experience 2.0 Apollo lane #150; business/source-of-truth #820 / #818. Do not modify or merge homepage PR #49 or original Research Desk PR #158; no WordPress activation is authorized.

## Actual implementation

`apollo-review-shortcode.php` is a **staging-only plugin adapter** exposing `[fv_apollo_review_custody]`. It reuses **the exact earlier R273/R276 review component** in the sibling `../apollo-r273` directory. Its default and only rendered state is editorial review pending. Shortcode attributes are intentionally ignored: a CMS author, URL parameter or attacker cannot claim an independent editorial approval by setting `state=approved`, `receipt_sha256`, or a merchant URL. No search engine robots settings, analytics, affiliate links, email, external media calls or WordPress writes are introduced.

The adapter handles ordinary singular posts and Gutenberg nested reusable (`core/block`) references with bounded depth (maximum eight) and cycle protection to enqueue the existing same-origin stylesheet in the head. For late/dynamic blocks whose presence cannot be known at `wp_enqueue_scripts`, it includes one **static same-origin stylesheet link in the rendered shortcode**; no inline script is needed. Missing component PHP falls back to plain HTML links to NASA and the free original investigation. This is a fail-open *historical-information* path, **not** a commerce/approval fail-open path.

IMPORTANT: the adapter assumes sibling `apollo-r273/review-custody.php` and `apollo-r273/assets/review-custody.css` have been installed together from the reviewed chain. No site is currently installed with these files; a WordPress lifecycle conflict could still exist. Inline preview CSS is exclusively for the QA fixture; no inline CSS is added by the plugin to production rendering.

## Exact tests executed (local, November 10, 2026 PT)

- `php -l experience2/apollo-r277/apollo-review-shortcode.php` — PASS.
- `php -l experience2/apollo-r277/qa/wp_contract_gate.php` — PASS.
- `php experience2/apollo-r277/qa/wp_contract_gate.php` — **20/20 logical scenarios PASS**, explicitly a WordPress API simulation, NOT installed WordPress.
- `python experience2/apollo-r277/qa/browser_gate.py QA-A` and repeat with `QA-B` — **14/14 contexts PASS on each run**, 320/390/768/1440/1920 JS/no-JS plus 320/390 200%/400% root text stress. Real Chromium tested the actual original rendered review PHP and the original print-corrected CSS, with native disclosure keyboard interaction, zero external browser requests, unique IDs, source URLs, no synthetic approval, two free CTAs and no commerce CTAs. Four screenshot pairs identical between independent runs. Receipt is reproducible; timing observations are separate volatile `lab_metrics.json`.
- The test does NOT establish true UI browser zoom, screen-reader, genuine axe-core, installed WordPress, live HTTP/CSP, Safari/Firefox or field LCP/CLS. Lab LCP/shift observations cannot stand in for real Core Web Vitals.

## Historical rights/source and conversion boundary

NASA Apollo 204 Review Board: <https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/>. The most probable initiator was electrical arcing; specific ignition source remained unproven. NASA advertising: <https://www.nasa.gov/nasa-brand-center/advertising-guidelines/>. Historical NASA hyperlinks do **not** grant commercial endorsement or image rights. No photos are added here, no geo pins/edges are proposed, and no new evidence claims are asserted.

**One hypothesis, not an activated funnel:** Grok verified Apollo long-form video with approved `asset_id`/UTM → existing public Atlas → free investigation → separately disclosed, relevant Mini Museum buying guide *only after merchant approval* → independently confirmed order and settled net revenue. No Grok Apollo published asset ID, owner-approved Mini Museum payable relationship, merchant settlement, consent-safe attribution, or confirmed paid order is established. The measurement contract is 7/30-day qualified-human sessions → one relevant CTA → confirmed lead if applicable → confirmed paid orders → gross less fees/refunds → **net revenue per 1,000 qualified human sessions**. No outbound click counts as a paid sale.

## Release blockers

Founder/independent editorial review of public Atlas pending statuses; actual packaged WordPress+Assembler install, real dynamic/reusable block asset load and HTTP/CSP; genuine axe-core with verified library provenance; screen-reader and actual browser zoom; full cross-browser device/touch; actual network failures; source/photo rights; CI on exact SHA; independent QD; verified Grok acquisition URL, merchant acceptance, and founder release authorization. Leave **DRAFT/HARD HOLD**. Do not post, activate affiliate links, install WP plugins, send mail or spend.
