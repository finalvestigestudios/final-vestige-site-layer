# R356 — no-JavaScript function/copy contradiction source gate

**Issue #136 · source of truth #820 · business charter #818. DRAFT / HARD HOLD / NO PUBLICATION.** This is an additive, read-only review gate stacked on R355 HEAD `db6d1e4da039b8066c583f2d4cae790969ac65e8`, not a production fix or QD determination.

## Authenticated source finding (already editorially identified in E349)

Original private Tool #104 `preparedness/content/tools/family-reunification-card.body.html` Git blob `be8698ac5d020476ff649d85813810e2000c6f98` tells readers in a `<noscript>` notice that the form still works with scripts disabled, while a later `<noscript><style>` block hides `#rc` and `#rc-warn` with `display:none`. The same notice mentions a text download that does not have an evidenced matching visible control in the inspected Tool #104 body. A separate blank fold-over print card is present in the no-script branch; this is **not** the same as an interactive no-script form. Do not infer real browser-print success from static HTML. The 7.5pt wallet-card typography needs physical-accessibility review.

Original metadata Git blob `47da1e7e20e39f0ea85e26d54a8d58301f6e0a15`; taxonomy `15c547bb3018ac182b12a51036389cfa39a59168`. The prior R355 privacy-promise hold also remains: no unconditional assertion that tab closure purges personal data or host/browser/print systems never transmit/save data. **No evidence of an actual data leak.** Qualified privacy and child-care review still required.

## New gate scope

- Detect no-script text's claim that the form functions versus source CSS hiding that exact form ID or class, missing no-script card, and unsupported download copy.
- Preserve citation declarations, original form identity, original embedded JS dependency markers, draft state and pending safety status.
- Hash-redact source/metadata; never inspect or emit entered visitor values. A native run reads only pinned original source and requires an authenticated local checkout with exact Git blob matches, no symlinks.
- Reject changed identities/claims/dependencies or false publish and safety states. Always return HOLD; there is deliberately no success exit code or release approval.
- Human owners must investigate actual browser behavior with scripts on/off, mobile widths 360/390/768 and desktop 1440, print page cropping and 7.5pt readability, network/storage/host scripts and session recovery. Reconcile instructions and source provenance without auto-editing risky advice.

## Verification evidence and honest limitations

**52/52 isolated synthetic Python tests PASS** on executable and test files with byte-exact Git blobs matched against GitHub, using `python -I -m unittest discover -s preparedness/tests -p 'test_r356_noscript_contract_hold.py' -v`. Compilation PASS. On an incomplete checkout, `python -I preparedness/tools/r356_noscript_contract_hold.py --repo-root <path>` rejects the run with `INVALID_HARD_HOLD`, exit 2. This is expected. Complete native `validate.py`, `build.py`, the full 36+ original suite, authentic 50 draft WordPress and 50 preview exports, and hosted CI are **NOT EXECUTED**. Isolated tests are not release readiness.

Original seven Claude + two Shelter branch SHAs checked against current GitHub branch collection; all nine still at the pinned R350 refs. Independent QD #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, synthetic fixture #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, downstream #2205 `bbcf1859768624c611df4abadc564c18247cf32a`, remain open and unmerged. No collateral changes to them. Homepage owner PR #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0` remains outside scope.

Original 15 editorial conflicts, 17 Article #15/Tool #104 review obligations, four disputed source identities and two tool-number collisions remain unresolved; 35 articles + six authored tools have not undergone authentic native integration in this run. No false QD pass.

## Conversion-first acceptance (ONE audience and one free destination)

**Audience/intent:** caregiver looking for a family out-of-area contact and reunification card after a related Grok family-contact social video. **Verified destination candidate:** existing public `https://finalvestige.com/preparedness/` (free Archive). Draft copy: **Start With Trusted Preparedness Resources.** **Optional private Tool #104:** NOT a deployable downloadable offer until no-JS, privacy, source, child-card and print review; do not gate free emergency planning. **Paid offer:** none authenticated as genuine, rights-cleared, payable and deliverable; NO PAID CTA. No retired water offer, unapproved SKU, affiliate activation or speculative sales claim.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / ACCEPTANCE EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Existing FV-owned Preparedness pack (not yet authenticated) | paid order | rights/active SKU, payment, delivery, refund terms unknown | Independently establish legitimate merchant offer and working delivery; check 360/390 mobile checkout, disclosures and refund terms | UNVERIFIED; no sales data | Founder/Commerce |
| Free family communications guide to optional Tool #104 | relevant resource CTA | two no-script contradictory promises, 7.5pt print, child privacy/source holds | Qualified editorial correction plus disabled-JS browser/physical print tests; never auto-publish | FAIL on source contradiction / browser NOT TESTED | Preparedness / QD / Claude |
| Authentic published Grok family-contact asset to existing Archive | qualified landing | published `asset_id`, linked destination and platform constraints unknown | Grok/Praxxis verify original asset, date, `utm_campaign`, `utm_content`, relevant CTA, permitted mobile route; do not change their production queue | UNVERIFIED | Grok / Praxxis |
| Qualified human sessions > relevant CTA > confirmed leads > independently confirmed paid orders > refunds/fees > realized net revenue | attribution and purchase | source-linked settled merchant receipts and 7/30-day deduplicated cohorts unavailable | Reconcile existing approved metrics, consent/confirmation/fulfillment; no duplicate tracking | NOT COMPUTABLE; zero asserted sales | Claude / Commerce |

**KPI on valid cohorts only:** realized net revenue per 1,000 qualified human sessions, with 7/30-day samples and small-n warning; paid conversion and lead-to-customer rates only when confirmations exist.

No merge, WordPress/CMS navigation or public changes, posts, emails, analytics installation, payments, spending, affiliate offer activation, creator queue edit or manufactured qualified safety approval.
