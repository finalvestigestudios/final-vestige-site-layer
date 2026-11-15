# Apollo Experience 2.0 R377 — Research Desk source roles (DRAFT, STAGING ONLY)

## The defect and why this is more important than another visual prototype

[Research Desk PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158) pairs six historical claims with six NASA photograph/archive identifiers. Its record #03 is titled **"Fourteen seconds changed the system"** and labeled an *instrument chronology*, yet its first archival image identifier is **S66-58038**, which NASA's official Apollo 1 gallery identifies as a 1966 crew photograph, **not telemetry**. The adjacent *Institutional research* link points to the proper Review Board report. The image has illustrative/context status, not documentary status for timing measurements. #06 likewise contains post-fire 102-test data in the card copy but links to a 2017 exhibit photograph and Board report rather than the [NASA 2018 flammability test account](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) that actually documents those tests. Original PR #158 is untouched.

R377 is an **isolated, accessible corrective source-role desk**: six explicit NASA-supported claim/limitation pairs, preserving case record order but distinguishing primary 1967 Board evidence, later NASA retrospectives and **photographic illustrations which do not prove the claim**. This is an independent review/component contract, not a claim that PR #158 has been patched or that production is safe.

## Source and copyright boundaries

- NASA's original [Report of the Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) supports ground-test, atmosphere, ignition uncertainty, chronology and hatch findings.
- NASA's [2022 retrospective](https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/) is labeled contextual, not primary.
- NASA's [2017 exhibit account](https://www.nasa.gov/history/apollo-1-crew-honored-in-new-tribute-exhibit/) documents displayed/revised hatch hardware, not real-time telemetry.
- NASA's [2018 flammability review](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) attributes **102 deliberate ignitions** to December 1967–February 1968 engineering tests of Boilerplate 1224, NOT the January 1967 fire.
- NASA [Apollo 1 gallery](https://www.nasa.gov/gallery/apollo-1/) identifies S66-58038 as a **1966 photo**, not an instrument record.
- NASA [Brand Center](https://www.nasa.gov/nasa-brand-center/) restricts identifiers, endorsements and some commercial uses. External NASA links do not authorize commercial photographs, logos or rights of publicity.

No images/videos, NASA insignia, geo coordinates, map edges, paid offer, affiliate links, tracking, mail or additional JavaScript are added. Evidence text and attribution remain free. Research roles (primary / retrospective / photo catalog) are explicit in accessible native <details> and printable source citations.

## WordPress staging integration (requires separate approval)

Isolated PHP file: source-role-desk.php; staging shortcode: [fv_apollo_source_role_desk_r377]. No WordPress data writes. It registers only if FV_R377_STAGING_ENABLED === true, FV_R377_APPROVED_HOST matches an HTTPS home_url on wp_get_environment_type() === 'staging', and the shortcode is unowned. It does not edit the primary R376 path, PR #158 or homepage #49. R377 deliberately uses a different shortcode to prevent collisions. Add to a controlled staging plugin only after owner authorization; **do not deploy** in production.

custody.json is pinned to SHA-256 60bfa330398b7684463c95afcc7e6ef347d44f22d5a2f1350286a660edb3a76f and must preserve six ordered records. Tampering or missing data withholds the claimed research and leaves one accessible free article link. CSS loads conditionally on directly authored singular content and **does not yet cover reusable blocks or nested resolved templates**; such cases are release blockers. No JavaScript is needed for source drawers, interaction or print.

## Reproducible executed tests

    php -l experience2/apollo-r377/source-role-desk.php
    python experience2/apollo-r377/qa/browser_qa.py
    python experience2/apollo-r377/qa/package.py --out /mnt/data/Apollo_R377_Evidence.zip

- **41/41 PHP stub checks** across six staging/host/collision/tamper scenarios, including photocatalog-source demotion, mutation rejection and fallback.
- **152/152 Chromium fixture checks** across ten actual headless Chromium contexts: widths 320, 390, 768, 1440, 1920; keyboard, touch, no-JavaScript, forced colors, reduced motion, 4× root-font and overflow.
- Real Chromium print: **3 pages**, official NASA Review Board and 2018 flammability document link targets, plus one free FV investigation destination. Document URLs are preserved in PDF even when native disclosures remain collapsed.
- CSS was adjusted in this run to keep **at least 200 CSS px of card paragraph width** at 320px/64px root font. That is an enlarged-root fixture stress test, not native 400% browser zoom.
- Local page.set_content measurements may yield LCP/CLS, but **are not site HTTP measurements or production Core Web Vitals**. Chromium navigation to file: and http: is blocked by this runtime; it is not represented as actual network navigation.

**Unverified, blocking:** installed WordPress/Assembler, real HTTPS CSP and stylesheet delivery, genuine axe-core (no offline distribution), manual screen readers, native 400% browser zoom, hosted exact-HEAD CI, consent/checkout attribution and commerce eligibility. No live or staging activation, review approval, paid service, or social content action.

## Conversion-first gate, not a new sales pitch

**Audience:** social-studies and history educators who arrive from an independently approved Grok Apollo documentary. **One next action:** free [Apollo 1 investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/). Potential original, rights-cleared educator dossier is a *hypothetical future* offer, not a verified available product; do not show checkout CTA until founder/Claude verify SKU, terms, payout and fulfillment. Grok retains script/distribution and Praxxis retains external creator review.

| OFFER → FUNNEL STEP | BLOCKER → CHANGE / EXPERIMENT → PASS/FAIL EVIDENCE | OWNER |
|---|---|---|
| Educator evidence kit → verified paid order | No authenticated payable, rights-cleared SKU, checkout or fulfillment; do not sell. BLOCKED | Founder / Claude |
| Grok Apollo video → qualified landing | Published asset_id/UTM and actual qualified-human sessions unverified; no analytics edits. UNKNOWN | Grok / Praxxis |
| Free NASA source-role desk → free investigation | Incorrect photo-as-instrument association clarified in source-controlled R377; PHP/Chromium PASS LOCAL ONLY | Apollo QA |
| Verified purchase → realized net revenue | Settled orders, refunds/fees, 7/30-day qualified sessions unavailable; KPI not computable. BLOCKED | Claude / Commerce |

No revenue or signup uplift claimed. Key KPI remains realized net revenue / 1,000 qualified human sessions, not clicks or pageviews. Coordination in [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) with cross-reference [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820); charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).
