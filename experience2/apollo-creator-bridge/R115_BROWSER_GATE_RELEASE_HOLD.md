# Apollo R115 — accessibility and conversion-path acceptance must fail closed

**Date:** November 4, 2026. **Status:** STAGING HOLD; do not merge/deploy. **Parent:** #150; conversion coordination #820; business charter #818. **Base:** R114 draft #927 at `0e94a47f19b88dc6b3fc21b351185ed09d31247a`. Distinct from original Research Desk #158, homepage lead, frozen PR #49 and production WordPress.

## Finding

The actual R114 Chromium runner allowed a receipt with `complete: true` when `--axe` was omitted: it treated axe as an optional scan. That condition must not be reported as accessible or release-qualified. Earlier evidence showed fixture browser successes but no actual source + required axe pass.

## R115 implementation (actual source, no live edit)

- `qa_r113_print.py`: do not label an acceptance receipt complete unless **all 14 real Chromium viewport/JS combinations**, the screenshot/PDF evidence, **six laboratory LCP/CLS observations**, and **four real axe scans** at 390px and 1440px across both full and filtered evidence states have passed. A missing local axe bundle now fails with explicit `AXE_BUNDLE_REQUIRED` and a non-green partial receipt.
- The same actual-page browser runner now invokes native Playwright touchscreen `.tap()`, verifies the free classroom CTA's keyboard **destination focus**, independently scrollable source register / no page-wide overflow, and reduced-motion behavior. It preserves JSON checkpoint receipts on failure.
- `landing-preview.html`: make focused source rows and the classroom destination visibly outlined; preserve no-JS access, and fail open when the evidence-filter status node is absent. The printed source-custody notice now includes NASA's official media/brand guidance link and explicitly does not clear any specific photo.
- `test_r115_failclosed_browser.py`: fourteen stdlib source-contract cases for the new fail-closed gate and source/commerce boundaries. These are intended to be *executed* in exact-head CI after infrastructure recovery.

## Tested versus untested (do not conflate)

**BUILT:** The actual HTML/QA runner changes and Python contracts are source-controlled on R115.

**TESTED:** 20/20 read-only exact-GitHub-blob structural assertions in the connector JavaScript inspection of committed candidate files (not Python execution). Verified HTML/runner/test Git blob IDs at the time of this report:
- `landing-preview.html` `c3c3d1aea0c628b950d6efdd0206e21ba83dfb32`
- `qa_r113_print.py` `b91f22dbc149e5d51b1116b50e4088af6c8a4a30`
- `test_r115_failclosed_browser.py` `beefc698de2dc3fdd87ff26dec75ba01203b55d4`

**NOT TESTED THIS SPRINT:** runnable Python unittest, Python compilation, actual-source Chromium, native touch and keyboard behaviors, four axe scans, new actual-page PDF/screenshots, six actual-page LCP/CLS trials, real WordPress.com/Assembler, physical-device WCAG, production CWV, or exact-head GitHub CI. The container/Python execution environment returned `redis.exceptions.ResponseError` repeatedly. This is a **tool infrastructure blocker**, not a product PASS. No axe bundle was supplied. Historical fixture evidence from R114 does not qualify R115.

**NOT VERIFIED:** six image-specific NASA permissions/rights assessments (0/6), proposed S67-19766 crew portrait association, proposed Apollo educator paid SKU and fulfillment/price/refunds, Grok Apollo asset/publish date or URL, attributed visitors, merchant orders, affiliate commissions, or net revenue. Separately published WordPress Evidence Atlas page 2017 is not this branch and its release authorization is not reconciled.

## Independent source/rights check

NASA's official brand center: https://www.nasa.gov/nasa-brand-center/ and advertising guidance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . Agency imagery/public records may be linked and often reused under policy, but source identity, third-party rights, recognizable-person publicity, commercial presentation and nonendorsement must be reviewed per item. **Do not equate outbound NASA links with rights clearance.** Original Research Desk draft #158 currently labels crew context as S67-19766 where R115 still treats that association as provisional; this cross-lane discrepancy must be resolved before any combined public release. No NASA photos are embedded here.

## Reproduction (requires a permitted local/offline runner)

```sh
python -I -m unittest discover -s experience2/apollo-creator-bridge -p 'test_r115_failclosed_browser.py' -v
python -I experience2/apollo-creator-bridge/qa_r113_print.py \
  --html experience2/apollo-creator-bridge/landing-preview.html \
  --out /tmp/apollo-r115-actual-source-evidence \
  --chromium /usr/bin/chromium \
  --axe /path/to/locally-approved/axe.min.js
```

If `--axe` is absent/unreadable, the browser runner must emit a **failure** receipt (not green). Do not fetch, install or activate unapproved third-party bundles; coordinate a pre-existing vetted local bundle and dependencies. Archive screenshots and generated PDF together with receipt, exact source SHA, browser version and hashes, with retention policy. Host WordPress/Assembler acceptance is an additional distinct gate and must not be inferred from `page.set_content`.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER

| Priority | Offer / funnel | Blocker | Change / experiment | Actual evidence | Owner |
|---|---|---|---|---|---|
| P0 | Proposed rights-cleared Apollo educator casefile → merchant order | No seller-origin live Apollo SKU, license/delivery/refund proof | Verify actual existing merchant offer; do not activate unverified checkout | NOT VERIFIED | Claude/Growth/founder |
| P1 | Future Grok Apollo long-form → source-led landing → **free** classroom exercise | CTA/touch/focus and source-row accessibility not browser-qualified | R115 focus improvements + fail-closed actual-page QA | BUILT, 20/20 source checks; browser NOT TESTED | Apollo; Grok owns distribution, Praxxis creator review |
| P2 | Free exercise → contextual product next action | No founder-approved relevant offer; no rights clearance | Keep free exercise sole CTA until verified merchant/founder gate | BLOCKED | Claude/Site QA/founder |
| P3 | Paid order → realized net/1,000 qualified human sessions (7/30 days) | No confirmed buyer, refund/fee or asset_id-qualified session data | Reuse #820 privacy-safe first-party attribution; zero new trackers | NOT COMPUTABLE | Claude/Growth |

## Release restrictions

No merge, publication, WordPress writes, merchant change, affiliate activation, content posts, paid service, duplicated tracking or homepage modifications. Hold for actual real-HTML Chromium/axe/performance receipt, independent WP/Assembler/screen-reader QA, historical source reconciliation, six photograph rights decisions, real approved saleable offer and founder decision. No speculative Atlas map pins or edges; no claim of Grok Apollo video being live.
