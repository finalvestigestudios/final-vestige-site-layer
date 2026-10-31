# Dispatch R28 — actual offline Chromium proof (NOT Jetpack MIME)

**Run:** October 31, 2026, after PR #358 creation. **Result: 24/24 PASS**, using local Chromium and Playwright Python in a sandboxed headless browser.

### What was actually tested

- Source: all six HTML preview files generated deterministically by the **current GitHub campaign renderer** `tools/build_previews.cjs`, against the same six source manuscripts independently SHA-compared with PR #351.
- Viewports: **320, 390, 768, 1440 CSS px**, each of six issues (24 independent cases).
- Method: `page.set_content()` of the locally stored preview HTML (file:// navigation blocked by sandbox administrator). No WordPress account, inbox, subscriber or real outgoing email was involved.
- Assertions per viewport: document and body `scrollWidth <= viewport + 2`; explicit "NOT A SENT EMAIL" hold; business-address and unsubscribe **unverified** markers visible; **zero** active merchant-buying links; Issue 03/05 nearby commercial disclosure visible; **zero** browser page errors.
- **All 24** satisfied every assertion. Three evidence screenshots at **320px** were captured for Issues 01, 03 and 05. Screenshot appearance shows the R20 fix for long disabled guide placeholders remains effective.

This adds browser-layout evidence beyond static source checks. It is not a simulated mail-client or a received WordPress message: Gmail, Apple Mail, Outlook and Jetpack can alter fonts/layout, strip CSS, truncate snippets, or inject footers differently.

### GitHub/WordPress continuity

- PR [#358](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/358) head `779ccbd9bda341099b87a5a21be721c5dd3a9329` **before adding this evidence file**, stacked on #351.
- Exact parent sources 17/17 SHA match; baseline local Python **134/134**; offline preview generation **13/13**; R28 isolated V8 source audit **73/73**; R28 regression assertions **26/26**, including 19 adversarial fail-closed mutations.
- The GitHub-hosted [run #41244852368](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41244852368) ended in **failure** with `steps=[]`. Hosted CI **NOT green**, and the cause is unknown. This browser run does not bypass the need for hosted CI or authorized real-email verification.
- Current WordPress newsletter enabled; new-post automatic email OFF; global excerpt setting; no sends. Actual received full-text MIME, final merchant offer-guide destinations and legal/commercial authorizations **NOT VERIFIED**.

**No publishing, sending, scheduling, WordPress write, merchant link activation or subscriber contact. All six HOLD_UNSENT; Issues 03 and 05 also HOLD_MERCHANT.**
