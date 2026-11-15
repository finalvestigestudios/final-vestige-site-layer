# Apollo Experience 2.0 · R378 — Reusable-block CSS custody

**STATE: SOURCE BUILT · LOCAL PHP API-STUB + ACTUAL CHROMIUM FIXTURE TESTED · INSTALLED WP NOT TESTED · DRAFT / RELEASE HOLD.**

## The evidenced defect

The independent, reviewed [R377 source-role Research Desk](../apollo-r377/source-role-desk.php) adds the stylesheet only when the top-level queried post's `post_content` directly contains the Apollo shortcode. A native WordPress `core/block` reusable block can render that same shortcode while the top-level post contains only a `ref`, leaving the source drawers and cards unstyled. This is a functional gap, *not* a statement that it was witnessed on an actual WordPress install. R370 addressed a different R369 component; it does **not** establish R377 coverage.

## Change / safety contract

- `guarded-reusable-assets.php`: **optional** staging-only WordPress companion that registers **no shortcode**, never overrides R377 or PR #158, and makes no WordPress writes. Registers one CSS pre-render enqueue action at priority 2 only after the approved R377 instance has registered its own exact shortcode handler. Requires R377's staging environment/HTTPS/host gate and existing shortcode ownership. No production fallback.
- Discovers the existing R377 shortcode directly or through nested `core/block` references to **published `wp_block`** posts. Read-only `get_post`/`parse_blocks` bounded at 6 levels, 200 blocks and 1 MiB fragments; rejects circular refs, unrelated post types and drafts. It intentionally does not claim coverage for theme template parts, dynamic server-rendered custom blocks, page builders, or all WordPress block patterns.
- Verifies adjacent R377 CSS bytes using exact SHA-256 `7a900dc0bf5e42fd527ccadddbed4d8f58138c87745ea96f55a991cda13bd8b3`; refuses symbolic-link substitution and any modified/missing CSS file. Uses R377's existing CSS handle so direct and reusable occurrences enqueue **at most once**.
- No new JavaScript, visual assets, NASA photographs/logos, external media, geographic claims, analytics, forms, Payhip transactions, tracking tags or unrelated CTAs. Original R377 source-role custody/print disclosures remain unchanged.
- **Do not install this plugin** unless founder/QD explicitly approve an independent *staging* installation; do not install alongside another competing Apollo alternative without reviewer approval.

## How to reproduce *local* QA

Requires local PHP 7.4+; Python 3, Playwright, Chromium, and pypdf. From the repository root, with sibling `experience2/apollo-r377/` present:

```bash
php -l experience2/apollo-r378/guarded-reusable-assets.php
python experience2/apollo-r378/qa/browser_qa.py
python experience2/apollo-r378/qa/package.py
python experience2/apollo-r378/qa/package.py # Must yield identical SHA-256
```

Results: `QA/results.json`; Chromium renders ten injected HTML fixtures at widths 320, 390, 768, 1440 and 1920, including no-JS, keyboard, pointer/touch, 4× root-font stress, reduced motion and forced colors. Print PDF verifies navigable Board, flammability and FV source destinations. The 15 PHP API-stub cases exercise direct/reusable/nested/duplicate refs, cycles, draft/foreign refs, unrelated content, production/host/disabled rejection, pre-owned shortcode, malformed large content, asset tampering and symlink substitution.

**Important limits:** These are API-stub fixtures with `page.set_content`. No actual WordPress/Assembler installation was accessed; Chromium HTTP navigation is blocked by the execution environment. Genuine axe-core distribution was not available offline, so no axe pass is claimed. No native 400% browser zoom, independent assistive technology, enforced HTTP/CSP, real network CSS waterfall, hosted CI, p75 field CWV, checkout, purchase or revenue test was executed. The root-font stress is not native zoom.

## NASA/source custody and commercial boundary

- Original Apollo 204 Review Board, NASA-hosted report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . The Board found no conclusively identified single ignition source; probable arc is **not** proof of a unique initiating wire.
- NASA, John Uri, 2018-02-14, *50 Years Ago: Apollo Flammability Tests*: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ . Documents **102 deliberate Command Module boilerplate ignitions in December 1967–February 1968**, after the January 1967 accident; not telemetry from the accident.
- NASA's NTRS metadata for the original Board report lists **US Government work, public use permitted** (https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19930078717.pdf). This is **not a blanket commercial clearance for NASA photographs, logos, or endorsement**. R378 adds **no reproduced NASA media**.
- The Research Desk source-role correction is held in R377 rather than modifying frozen Research Desk PR #158. In particular, PR #158's crew photo S66-58038 cannot prove instrumental telemetry.

## Conversion-first, release-gated user path

A Grok-owned, source-reviewed Apollo documentary (only after asset ID/actual publication verified) → NASA source-role desk / evidence atlas → **single existing free Apollo investigation link** → optional later verified *educator evidence kit* if rights, payable SKU, checkout, fulfillment and founder approval are established. R378's observable improvement is reliable styling for a reusable-block surface, **not a paid conversion result**. Neither Jetpack views nor clicks prove customer payments.

| Offer → funnel | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|
| Educator dossier → checkout | No approved, rights-cleared payable SKU | Withhold paid CTA pending real product/checkout verification | Purchase NOT VERIFIED | Founder / Claude |
| Grok documentary → landing | Published Apollo asset ID and UTMs unconfirmed | Use approved unique `utm_content=asset_id`; no duplicate script | Human sessions NOT VERIFIED | Grok / Praxxis / Claude |
| NASA evidence desk → free story | Reusable block could render without R377 CSS | Conditional pre-render CSS custody add-on | PHP 117/117, Chromium 142/142 local fixture PASS | Apollo QA |
| Confirmed orders → realized net revenue | Merchant data, refunds, fees, cohorts unavailable | Match qualified 7/30-day users to **merchant-confirmed** sales only after approval | KPI NOT COMPUTABLE | Claude / Commerce |

`net revenue per 1,000 qualified human sessions = 1,000 × (settled paid revenue − refunds − processing/other directly attributable fees) / qualified human sessions`; do not calculate without both a valid denominator and verified merchant numerator. No signup/purchase claims.

## Release blockers

Real approved WordPress/Assembler staging host, verified shortcode insertion in live reusable blocks, actual HTTP CSS timing/CSP, independently installed axe-core plus screen readers, native zoom, hosted CI on exact PR head, approved NASA media permissions if later used, payable product/merchant acceptance, and founder/QD authorization. Homepage PR #49, lead homepage lane, Research Desk PR #158, Grok-owned creative, Praxxis review, and existing TASK-008 Drive queues are untouched.
