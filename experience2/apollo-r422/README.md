# Apollo Experience 2.0 — R422: exact-head artifact custody and staging acceptance

STATUS: DRAFT ONLY — PRODUCTION HARD HOLD. Isolated staging QA/reconciliation code under experience2/apollo-r422; stacked on R421. No edits to homepage PR #49, Research Desk PR #158, Grok or Praxxis TASK-008, WordPress, merchant or analytics.

## New finding: four R417 files do not match the tested archive

GitHub source blobs read at exact R417 PR #2803 commit a088077d8a58c0e10842bbd48d2da9d6d65b00e8 disagree with the R417 QA ZIP in four out of seven source entries: README.md, qa/test_browser.py, qa/test_provenance.py and staging-provenance-guide.php. The other three entries agree. Its prior locally reported 17/17 and 15/15 passes do not establish that the committed R417 code was tested. R417 cannot be released on those local receipts.

A separate control of the R421 source ZIP against PR #2822 exact commit 7f0d20cb9e4fdfefbdd569da7cab3097c0fc7bc4 finds 9/9 source entries identical. That is an archive-identity PASS only. It does NOT validate the earlier R417 code or grant WordPress, release, accessibility or commercial approval.

## Run the independent source identity gate

python qa/test_identity.py

python qa/archive_identity_gate.py --release r417 --archive /path/to/R417-local-QA.zip --output QA/r417-identity.json
# expected exit 2: four source discrepancies, HARD HOLD

python qa/archive_identity_gate.py --release r421 --archive /path/to/R421-local-QA.zip --output QA/r421-identity.json
# expected exit 0: artifact identity only; production remains HARD HOLD

The test computes actual Git blob SHA-1 identities from archive bytes. It rejects missing, duplicate, extra or mismatched source entries and deliberately ignores generated QA/ log claims. The immutable expected identities are recorded in qa/manifest.json from authenticated GitHub source reads; update only after an independently reviewed new commit. This is not a general GitHub network client and needs no new credentials or paid services.

## Browser release gate — executable but not yet runnable against real staging

qa/staging_browser_acceptance.py is a read-only real-navigation Playwright Chromium harness that requires an explicitly approved nonproduction HTTPS hostname AND locally provided genuine axe-core JS pinned to an independently reviewed SHA-256. It refuses public finalvestige.com and www.finalvestige.com. It tests the installed R421 source-receipt experience at seven widths (320, 360, 390, 768, 1024, 1440, 1920), exactly three source receipts, one free Apollo 1 investigation CTA, no unauthorized embeds/forms/maps, zero overflow, real axe-core WCAG rules, keyboard/touch/no-JS/forced-colors/zoom/reduced-motion checks, same-host network isolation and browser-observed navigated laboratory LCP/CLS. It writes screenshots and a JSON receipt; no scripts are installed on WordPress or existing analytics. Its timings are lab samples, not field p75 CWV.

Command example (ONLY after staging owner provides target and vetted axe JS):
python qa/staging_browser_acceptance.py --url https://APPROVED-STAGING-HOST/path --approved-staging-host APPROVED-STAGING-HOST --axe-js /trusted/axe.min.js --axe-sha256 REVIEWED_64_HEX_SHA256 --output-dir QA/staging

This runtime blocks Chromium navigation (ERR_BLOCKED_BY_ADMINISTRATOR); no vetted axe-core file, installed R421 staging URL or actual end-to-end test evidence is available. Therefore genuine axe results, navigated LCP/CLS, screenshots of installed WordPress and QD review remain BLOCKED. No inflated PASS or faux performance metrics.

## One creator-to-customer path; commerce held until verifiable

Verified Grok Apollo asset (actual post URL, asset_id and approved UTMs required) → NASA evidence receipts/Atlas → existing free Apollo investigation https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ → separately founder-approved, rights-cleared, actually purchasable original teacher evidence dossier. No fictitious SKU or paid CTA. This sprint adds no live page, media reuse, tracking, email, post or product.

Source proof: NASA Apollo 204 Review Board https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ did not conclusively establish the ignition initiator. NASA https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ dates the later 102 deliberate Command Module ignitions to Dec 1967 through Feb 1968. Keep photo dates and source limitations separate, and never invent geographic pins.

OFFER → FUNNEL STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER
1. Original educator dossier → confirmed paid order → no verified rights, active SKU/checkout/fulfillment → withhold paid CTA and validate genuine offer → HOLD → Founder + Claude.
2. Grok video → qualified landing → published asset ID/actual post URL and attributable human sessions absent → request via existing TASK-008 only → UNVERIFIED → Grok + Praxxis.
3. Source receipts → free investigation → upstream R417 code/evidence drift → pin exact HEAD and run staging browser suite → R417 FAIL / R421 identity PASS / staging BLOCKED → Apollo QA + independent QD.
4. Confirmed orders → realized net revenue / 1000 qualified human sessions → no independently verified merchant sales, fees/refunds or 7/30-day human-session cohorts → NOT COMPUTABLE → Claude + Commerce.

No production release, merge, WordPress modification, posting, spending, e-mail or checkout activation is authorized. Founder approval and exact-head CI/QD remain mandatory.
