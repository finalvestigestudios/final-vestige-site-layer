# Apollo R117 — Offline delivery-boundary guard / conversion trust gate

**Date:** 2026-11-04 (Pacific) · **Staging only** · Parent issue #150; business charter #818 and conversion issue #820. **Branch:** `qa/apollo-r117-offline-privacy-funnel-boundary-20261104`. **Base:** R116 commit `31f212c9ddc112638d55a924713f376808e3c487` / draft PR #939. This is an additive independent Apollo lane, not a homepage, CMS or merchant change.

## Concrete regression / why it matters

The R116 NASA custody validator checked direct photo URLs and banned several obvious forms and payment links, but it did not inspect the other outbound links or local inline script/style behavior for remote-resource or client-side visitor-capture additions. A third-party campaign redirect, a second tracking vendor, a CSS remote request or an unauthorized purchase link could be introduced without triggering that custody contract. This was an **uncovered QA risk**, not a claim that any such tracker exists on production.

**BUILT:** `qa_r117_delivery_boundary.py` is a deliberately restrictive offline check for the isolated Apollo landing. Its exact-host allowlist permits NASA official pages (including `sma.nasa.gov`), FV article links and internal fragments; disallows misleading suffixes, URL queries, schemes, userinfo and ports. It fails on network-capable tags and most injected commerce/capture markup, CSS remote loads, event-handler attributes, scripts with common network/storage/injection APIs, additional primary CTAs and removal of the photo-rights uncertainty notices. It returns an explicit `STAGING_HOLD`, never a sales or browser pass.

**LIMIT:** This is regression source lint, **not a security sandbox**, exhaustive JavaScript static analysis, proof that actual web requests cannot occur, NASA file-specific rights clearance, an automated consent audit or a replacement for Playwright/axe/physical-device acceptance. Deliberate obfuscation can bypass token checks; browser network interception/CSP review is still required. There is no new analytics script, checkout, form or email action.

## Reproducible tests / source

```bash
python -I experience2/apollo-creator-bridge/qa_r117_delivery_boundary.py \
  --html experience2/apollo-creator-bridge/landing-preview.html
python -I -m unittest discover -s experience2/apollo-creator-bridge \
  -p 'test_r117_delivery_boundary.py' -v
python -I experience2/apollo-creator-bridge/qa_r116_nasa_custody.py
python -I experience2/apollo-creator-bridge/qa_r113_print.py \
  --html experience2/apollo-creator-bridge/landing-preview.html \
  --out /tmp/apollo-r117-real-page \
  --chromium /usr/bin/chromium --axe /path/to/approved/axe.min.js
```

**TESTED locally:** 22/22 regression and negative-control tests passed on the corresponding offline Python implementation and fixture in the local execution environment. **Exact-GitHub-source read-only structural QA:** staging page had 28 hyperlink references, all with same-page targets or approved NASA/FV HTTPS hosts; 1 primary free CTA, 1 inline script, 1 inline style; 0 `img`, `form`, `iframe`, external `link` or `svg` tags; 0 detected `fetch`, `XMLHttpRequest`, `sendBeacon` or storage terms in the inline script. These observations do not constitute an actual execution of the new GitHub validator against the full landing or a browser security assertion.

**NOT TESTED on exact GitHub R117 head:** hosted Python suite; combined R116/R117 validator against actual page; real Playwright 320–1920 seven-width JS/no-JS matrix, axe four acceptance scans, actual landing LCP/CLS, genuine WordPress/Assembler, keyboard/VoiceOver/NVDA physical devices, merchant checkout or Grok campaign attribution. No new screenshots or Core Web Vitals claims. Existing live Atlas page approval-state reconciliation remains unresolved.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL EVIDENCE → OWNER

| Priority | Offer and funnel | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|---|
| P0 | Proposed paid Apollo teacher casefile → merchant-confirmed order | Existing matching sellable SKU, price, licensing, delivery and refund behavior **not independently verified** | Claude/Growth to read seller-origin inventory and merchant receipts; do not introduce a checkout until source and rights pass | **BLOCKED; no verified orders** | Claude / Growth / founder |
| P1 | Approved Grok long-form Apollo asset_id → source-led investigation → free classroom exercise | Poor trust if unsolicited redirects/trackers appear in a primary-source educational landing; genuine browser QA pending | R117 restricts staging delivery boundary, retains **one** source-aligned classroom CTA | **BUILT; 22 local fixture tests and exact-source structural checks, full-page browser NOT TESTED** | Apollo; Grok posts/scripts; Praxxis reviews |
| P2 | Free classroom exercise → relevant rights-cleared paid resource | Product and founder authorization missing | Keep paid link disabled; only test approved contextual offer after evidence | **NOT VERIFIED** | Claude / founder |
| P3 | Paid orders less refunds/fees → net per 1,000 qualified human sessions (7/30 day) | No independently linked Apollo Grok asset_id sessions, purchases or merchant reconciliation | Reuse #820 event/UTM contract; no duplicate scripts | **NOT COMPUTABLE** | Claude / Growth |

**Research Desk #158:** read but untouched. It has separate shortcode/asset-loading and provisional `S67-19766` confidence discrepancies. The six NASA photographic-reuse assessments remain 0/6 complete and unconfirmed crew ID stays provisional. No geographic pins, invented relations, NASA image binaries or posted Grok content.

**RELEASE: STAGING HOLD.** The founder has not approved Apollo commercial activation or this branch's production deployment. Homepage frozen PR #49 and Claude engineering branches untouched; no WordPress content/settings writes, marketing posts, email sends, purchases or paid services. Exact-head CI and independent rights/editorial/WordPress/browser acceptance and publication authorization are mandatory.
