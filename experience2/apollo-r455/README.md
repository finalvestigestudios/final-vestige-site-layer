# Apollo Experience 2.0 — R455 evidence and claims crosswalk

**State:** BUILT + TESTED OFFLINE; **NOT INSTALLED, MERGED, LIVE, OR VERIFIED ON WORDPRESS STAGING**. Standalone additive R&D staging candidate, stacked on R454 PR #2999. Ownership: Apollo research/QA under #150, Research Desk #158 (do not modify), commercial attribution #820, business charter #818. No changes to homepage PR #49, homepage lead, Claude's core site/analytics/commerce or Grok/Praxxis TASK-008.

## What is distinct in R455

`[fv_apollo_crosswalk_r455]` creates a source-led chronological claim challenge: four NASA official source records, distinct **event/caption/publication date roles**, clearly paired **what source supports / cannot establish** fields, citation-and-rights drawers, and an original teacher-facing misleading-certainty exercise with a sourced answer rubric. All four records and the answer are available with JS disabled. Optional JS filters by evidence role, exports an **original text-only note entirely in the browser** (no server), and announces selection changes. No photos, marks, speculative pins, map edges, affiliate links, purchase buttons, data capture, tracking scripts, new analytics or third-party dependencies. Exactly one context-relevant CTA leads to the existing free full investigation.

The PHP explicitly requires `FV_R455_ENABLE_STAGING === true`, an `FV_R455_STAGING_PAGE_ID` positive integer, `wp_get_environment_type() === 'staging'`, and the exact queried page ID. It is not installed/activated by the PR. The two bundled assets must match SHA-256 digests or the shortcode falls back to a readable link. Never enable in production. This is a separate candidate, not a modification of original Research Desk source.

## Original authoritative sources (checked 2026-11-18)

- NASA, **Report of the Apollo 204 Review Board**: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — finding of most probable electrical-arc initiator and explicit nonidentification of a single conclusive ignition source; review issued after Jan 27, 1967; do not label accident date as publication date.
- NASA, **Apollo 1 Gallery**: https://www.nasa.gov/gallery/apollo-1/ — dated Oct 18, 1966 crew-preparation caption; source links only, no image reuse.
- NASA, **2017 tribute release**: https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/ — Jan 27, 2017 memorial with hatch; a later interpretive exhibit.
- NASA, **2018 flammability retrospective**: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ — Feb 14, 2018 retrospective on 1967–68 follow-up trials, not the original fire initiator.
- NASA, **Media Usage Guidelines**: https://www.nasa.gov/nasa-brand-center/images-and-media/ — NASA website images can contain protected third-party material; branded advertising/promotion/identifiable people may require clearances. No endorsement.

External source verification proves source identity and scope, NOT rights clearance or editorial signoff. No NASA images/diagrams reused.

## Local test receipts and limitations

`php -l apollo_crosswalk.php && python qa/test_contract.py && python qa/browser_qa.py`.
- **19/19** PHP/source/rights/guard/adversarial tests PASS.
- **23/23** Playwright Chromium actual interaction cases PASS against PHP-produced HTML in `page.set_content()`: widths **320,360,390,768,1024,1440,1920** JS enabled/disabled; real touch and keyboard activation, independent shortcode instances, no-JS source disclosures, 200% zoom, forced colors, reduced motion, print and actual browser text download.
- Staged PHP/CSS/JS integrity/fallback and exact page guard verified offline. Screenshots and deterministic QA archive generated locally.
- **NOT RUN**: real-host navigated WordPress staging, genuine axe-core, navigated LCP/CLS, Safari/VoiceOver/NVDA, p75 field CWV, INP, exact-head hosted CI. The sandbox blocks Chromium navigation to URL/file targets with `ERR_BLOCKED_BY_ADMINISTRATOR`; axe-core is not preinstalled and npm cannot access registry. `qa/staging_gate.py` is a source-controlled *future* real navigation/axe/lab performance runner: requires explicitly approved HTTPS staging URL and reviewed local axe-core JS; it fails closed without both. Do not substitute offline metrics for real staging CWV.

## Commercial release gate (conversion first)

**Single proposed audience:** history teachers/home educators who arrived from a genuinely published, source-matched Grok Apollo long-form asset. **One route:** verified Grok post and asset_id/UTM (not presently proven) → Evidence Atlas source comparison → original no-signup teacher exercise → free Apollo full investigation → separate *proposed* original rights-cleared educator kit only once authentic SKU/checkout/fulfillment and founder approval are established. No paid CTA while offer is unverified. This candidate makes a *trust-to-purchase hypothesis*; it does not create a sale, lead, or verified attributed human session.

Prioritized `OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER`:
1. Proposed educator kit → verified purchase: payable rights-cleared SKU, checkout, delivery, refunds unverified → withhold paid CTA → HARD HOLD → Founder + Claude Commerce.
2. Grok Apollo video → qualified human landing: no independently verified published asset_id, mobile post route or per-asset human denominator → do not assign invented UTMs → UNKNOWN → Grok + Praxxis / Claude analytics.
3. Source comparison → free investigation: misleading historical certainty / lost context → add paired evidence limits, source drawers, original exercise, one free CTA → offline PASS, staging HOLD → Apollo + independent QD.
4. Purchase → realized net revenue per 1,000 qualified sessions: settlements, fees, refunds, 7/30-day cohorts absent → no revenue claim → NOT COMPUTABLE → Claude Commerce.

**Production HARD HOLD** until R417/public Atlas discrepancies resolved, genuine staged QA, independent QD/editorial/rights review, exact-head CI green, verified product/customer attribution, and founder approval. No production release/WordPress writes/social publication/affiliate activation/spending.
