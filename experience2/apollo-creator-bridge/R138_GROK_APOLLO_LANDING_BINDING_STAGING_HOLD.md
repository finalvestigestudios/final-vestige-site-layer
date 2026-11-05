# Apollo R138 — source-independent Grok asset → Apollo landing binding
**2026-11-05 · STAGING ONLY / RELEASE HOLD.** Governing engineering issue #150; conversion #820 and charter #818. R138 is stacked on R137 draft #1071, not on frozen homepage #49 or independent Research Desk #158.

## Reproduced defect
The R137 helper could validate the *syntax* of a first-party referral URL, but the R136 conversion gate never invoked that helper or compared the intended UTM destination against an independently reviewed WordPress permalink. A caller could submit an internally plausible Grok video candidate pointing to a different Final Vestige article. `destination_reviewed: true` alone did not bind asset, target and approved route.

## Actual isolated fix
- `r138_creator_landing_custody.cjs` binds the supplied YouTube watch/Shorts/shortlink video ID to an explicit `youtube_video_id` and checks the creator URL, the `asset_id`-specific four-key UTM landing URL, and the exact independently supplied first-party route.
- A known/reviewed `reviewedLandingUrl` must be given **separately**, through the QA assessor; the campaign object cannot self-declare its reviewed permalink. Canonical first-party HTTPS, no query/fragment, no home-page destination, no alternate article or redirect.
- `r136_conversion_evidence_gate.cjs` now refuses to treat a campaign as even a document-only candidate without this binding. It does not approve social publication or commercial activity.
- Existing R136 test fixtures and 12 new adversarial test cases cover missing canonical permalink, malicious lookalikes, unrelated articles, wrong video ID, duplicate UTMs, query injection/PII, Shorts, youtu.be, and empty inputs.
- No guessed live Apollo permalink is hard-coded. `https://finalvestige.com/investigations/apollo-1/` occurs **only as a synthetic test fixture** and must never be described as a verified/live route.

## Test custody
New module Git blob `ce17aeb1b890dce64fa57ef88513ea72d922b5a8`; new native test Git blob `f0614c00a24f57f8661339b2a3ebfad46d20fdfb`; existing R137 dependency Git blob `f5c2351f7b7cd53735df28f54ccab90f0c2962cf`. The exact Git-blob-matched files were executed locally with Node v22.16.0: **12/12 PASS, 0 FAIL**. Existing R136 converter and updated R136 regression tests were source-inspected, but **not executed in native Node in a complete repository checkout**. Complete R133 deterministic source build, actual-page Playwright, axe-core, LCP/CLS and WordPress/Assembler integration remain NOT EXECUTED. In the available browser sandbox, Chromium navigation returns `ERR_BLOCKED_BY_ADMINISTRATOR`; no full-page acceptance or screenshot claim is permitted.

Native reproduction in a complete checkout:
```sh
node --test experience2/apollo-creator-bridge/test_r138_creator_landing_custody.cjs
node --test experience2/apollo-creator-bridge/test_r136_conversion_evidence_gate.cjs
node --test experience2/apollo-creator-bridge/test_r137_destination_integrity.cjs
node experience2/apollo-creator-bridge/r134_actual_page_browser_acceptance.cjs --out /tmp/apollo-r138-real-browser
```

## One source-led landing-to-product hypothesis
Grok **owns** the YouTube long-form/Shorts script, asset IDs and distribution; Praxxis owns creator QA. No Apollo YouTube post or asset_id was independently verified. Prospective high-intent segment: grade 6–9 educators using credible primary-source analysis. Proposed journey: **verified Grok asset** → **reviewed Apollo investigation route (TBD, no fabricated URL)** → single nonintrusive **free source-analysis worksheet** link (`#classroom-preview`, readable with JS off). This establishes source trust before asking for paid demand. A teacher-ready casefile is **only a proposed offer**; no Apollo-specific Payhip SKU, actual listing, fulfillment, license or refundable paid order has been independently verified, so **do not insert a purchase CTA** or offer price. Keep the six NASA photographs external-only until 6 individual reuse assessments are signed. A proposed product must contain original pedagogical work and verified rights.

### OFFER → FUNNEL STEP → BLOCKER → CHANGE / EXPERIMENT → EVIDENCE → OWNER
| Offer | Funnel step | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|---|
| Prospective educator casefile | Video → Apollo | Source and intended article were not bound | R138 reviewed-route + video-id + UTM custody | **BUILT; 12/12 new native tests PASS; live URL unknown** | Apollo engineering; Grok and Praxxis content review |
| Existing free worksheet | Apollo → resource | No real multi-width browser acceptance | Run R134/R135 true-navigation + axe at 320/360/390/768/1440/1920, no-JS, keyboard/touch/reduced-motion, check LCP/CLS with lab/p75 labels | **BLOCKED: Chromium administrator policy; no WP staging** | Apollo QA; Claude for integration |
| Future paid lesson kit | Resource → checkout | No verified relevant existing sellable product or photo reuse scope | Audit actual inventory, rights, delivery, refund policy with owner approval before any contextual CTA | **NOT VERIFIED; 0/6 photo reuse cleared** | Claude Growth / Founder |
| Confirmed paid order | Purchase → realized net revenue | No independently attributed human session, settled order, fee/refund data | Existing #820 privacy-safe 7/30-day cohort contract only; no duplicate script | **NOT COMPUTABLE / no verified sale** | Claude Analytics |

**Key KPI:** net realized revenue / qualified human sessions × 1000, reported only with nonzero evidence-based denominator and reconciled confirmed orders, refunds and fees. CTA click ≠ lead, checkout start ≠ paid order, and synthetic `utm_content` ≠ actual Grok publication.

## Release gate — CLOSED
Require real reviewed production/staging Apollo permalink, Grok-published asset+asset_id evidence (if campaign activation considered), exact-head native CI, actual-page keyboard/touch/no-JS/axe/visual screenshots and independent performance evidence, Research Desk editorial source signoff, WordPress compatibility, all six individual media-rights assessments for any reuse, verifiable paid inventory and founder approval. No deployment, marketing post, CMS settings/content write, tracking vendor, checkout activation or expenditure authorized. No invented pins/map edges.
