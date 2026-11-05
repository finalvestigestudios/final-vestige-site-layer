# Apollo R134 — actual-page Research Desk browser gate (STAGING HOLD)

Governing issues: #150, #820, #818. Built on the R133 unpublished offline source preview. Does not edit original Research Desk PR #158, frozen homepage PR #49, WordPress, analytics, merchant, social or email systems.

## Exact change
The new r134_actual_page_browser_acceptance.cjs runner first executes the complete-source R133 build, starts an HTTP server returning its exact HTML bytes, and *requires* Chromium page.goto to navigate to that URL. A local server 200 is not a browser PASS. No page.setContent shortcut is permitted. Unexpected remote requests, missing evidence, unmeasured performance and browser policy failures fail closed. The stdout and receipt never imply production readiness.

## Run in an unrestricted full repository checkout
Requires already-approved local Playwright, Chromium and axe-core installations. This script never installs or downloads dependencies or triggers billable CI. For a nondefault Chromium executable, set FV_CHROMIUM_EXECUTABLE.

    node --test experience2/apollo-creator-bridge/test_r134_actual_page_browser_acceptance.cjs
    node --test experience2/apollo-creator-bridge/test_r133_build_research_desk_preview.cjs
    node experience2/apollo-creator-bridge/r133_build_research_desk_preview.cjs --out /tmp/apollo-r133-confirm
    node experience2/apollo-creator-bridge/r134_actual_page_browser_acceptance.cjs --out /tmp/apollo-r134-qa

The runner writes r134-test-receipt.json and returns exit code 2 on failure or missing dependencies.

## Test coverage designed; NOT claimed executed
- Real HTTP 200, exact served source digest/equality, URL match, unexpected network requests, page errors.
- Screenshots at 320/360/390(touch)/768/1440/1920 widths; viewport overflow; six evidence cards and six NASA source links.
- Search initializes, no-hit state, Escape reset, clear button pointer/touch click, focus restoration.
- JavaScript-disabled 390px reading: all six records and links present, search tools hidden.
- Buffered PerformanceObservers installed before navigation for local LCP and CLS. Missing readings fail; lab targets LCP <=2.5s and CLS <=0.1, NOT real-user p75 or measured INP.
- axe-core WCAG 2 A/AA, 2.1 AA and 2.2 AA at 390 and 1440. Dedicated axe context bypasses preview CSP solely for local audit injection; standard navigation test retains CSP.
- The source-controlled native Node tests verify localhost route containment, noindex/nosniff/no-store/no-referrer and fail-closed release metadata without requiring Playwright.

Screenshot bytes can vary by browser/OS versions; the generated HTML and its SHA-256 manifest are designed to be deterministic. The QA receipt records provenance and results, not invented success.

## Remaining gates
Run on a full repository checkout on a machine allowing actual Chromium HTTP navigation (prior environments reported ERR_BLOCKED_BY_ADMINISTRATOR). Even after browser tests pass, obtain actual WordPress/Assembler tests, screen-reader and zoom tests, manual mobile touch inspection, production CWV/INP where available, independent historical review, individual NASA photo reuse clearance (still 0/6), editor signoff, relevant merchant SKU verification, and founder production authorization. The proposed crew portrait S67-19766 identification is provisional.

## Conversion-first decision table

| OFFER → STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Existing educator-compatible SKU → merchant-confirmed paid purchase | Existing Apollo-specific Payhip item, rights, price, fulfillment, fees and refunds unverified | Read-only verified inventory; no invented purchase CTA | BLOCKED; no confirmed orders | Claude/Growth + founder |
| Grok Apollo long-form → source proof → free worksheet | No actual-page browser/axe/performance acceptance | R134 real navigation, six widths and no-JS checks | BUILT; actual Chromium run not executed in this sprint | Apollo Studio + independent QA |
| Free worksheet → optional paid kit | No approved matching item or founder approval | One relevant, nonintrusive product link only after approval and independent rights/merchant validation | NOT ACTIVATED | Founder/Claude |
| Verified sale → net revenue per 1,000 qualified sessions | No reconciled attribution, orders, fees or refunds | Existing privacy-safe #820 measurement; 7/30-day cohorts | N/A, not zero | Claude/Growth |

Flagship: Apollo 1: Fourteen Seconds, More Than One Failure, proposed for Grok long-form/Shorts; NOT represented as published. Audience: secondary teachers. One current contextual action: Review the free classroom evidence exercise. NASA Apollo 204 Review Board provides the technical primary account, while six NASA photograph links provide visual context, not instrument readings or reuse permission. Preserve free historical record, no ads or commerce inside chronology. Grok owns production and posting; Praxxis independently reviews via TASK-008. No newsletter, visitor tracking, merchant, CMS or content-queue changes in R134.

RELEASE: STAGING HOLD. Do not merge or deploy from this result.
