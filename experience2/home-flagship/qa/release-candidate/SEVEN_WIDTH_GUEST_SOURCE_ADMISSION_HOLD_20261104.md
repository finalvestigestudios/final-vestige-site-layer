# Seven-width genuine-visitor source / no-JS admission — draft / HOLD
**November 3 PT / November 4 UTC 2026.** Stacked on draft PR #906 exact base `086de3ab1d07fb1c495907f8c3aee738eda68bba`. Frozen #49 untouched.

## Actual defect and conversion relevance
The existing new anonymous-visitor harness checks only **five** widths (360, 390, 768, 1440, 1920), validates **72 DOM nodes but not their published texts**, and treats an existing no-JS `<details>`/Focus anchor as sufficient even if its content is CSS-hidden. Its `DOMContentLoaded` screenshot does not await the fonts or decode first-viewport images. That is weaker than the founder's 320–1920 evidence-first, no-JS, reliably painted mobile visitor contract. A false-positive visitor test can lead to a broken Focus conversion path being approved. These defects were inspected in actual source on #906, not inferred from an image.

## Engineering change — isolated branch, no site writes
- Seven anonymous visit widths: **320, 360, 390, 720, 768, 1440, 1920**. The 720×450 case is only a CSS viewport **proxy** for 200% desktop zoom, NOT physical zoom certification.
- Compare **all 72** guest DOM text fragments in order with the vetted **public page 6** fixture, not merely a count. Load and validate fixture before running local-copy PHP.
- At every width, await document fonts and decode visible first-screen images **before taking screenshot**; a decode failure is recorded as an explicit HOLD, while still saving the screenshot for inspection. This is not a substitute for the established media-body SHA/transfer/decoding test in the separate authenticated 1440px runner.
- In the JS-disabled anonymous view, fail if source disclosure, contextual free Fieldbook link or Margins are hidden by CSS; require 72 Margins in static document flow, opacity 1, scrollable region and no horizontal overflow, and validate all actual public texts. Keep 2 historical links.
- Existing clean guest authentication, 44×44 unobstructed CTA, native Tab order, full-document axe scan, temporary loopback copy cleanup and strict external-network restrictions stay in place. No instrumentation or merchant traffic added.
- Wiring to existing isolated Assembler CI includes 6 unit tests; the mutation test rejects **72/72** individual historical-text changes and the no-JS matrix rejects **12/12** invalid states.
- `guest_render_source_contract.mjs` and `test_guest_render_source_contract.mjs` are independently Node-runnable. No new npm dependency.

## Evidence and exact-source fidelity
**Executed locally** with Node 22: `node --check` on both newly added source/test files; `node --test test_guest_render_source_contract.mjs`: **6/6 PASS**. This includes 72 text-tamper attempts and 12 no-JS defect cases within those six tests. Local source bytes checked against actual GitHub blobs, exact:
- helper blob `a792daf9243375e6e6c1e9c869145f5e202b6fc9`
- tests blob `54ba1b493f5ec6b91dc34fd3a24fb106b41184f3`

**Source reviewed, NOT executed in WordPress/Playwright:** changed existing `isolated_guest_render_gate.mjs` (blob `8e39292ad1bd0c32017f35745c49279e530c2865`), including 7-width loop, margin assertions, image decode and no-JS assertions. The GitHub workflow is updated to run the new tests (blob `4482b0ee840091402f4ff93b445035504dc25686`). **Full exact-checkout integration and HTML/browser/axe/Lighthouse tests remain unverified; latest GitHub Actions on parent PR #906 failed before steps.** Do not count the isolated Node test as a WordPress test or an accessibility certificate.

## Commercial / ownership decision
| Offer | Funnel | Known blocker | This change/experiment | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Free 52-page Focus Fieldbook | Grok Mind visitor → flagship observer → free Focus CTA | Prior guest gate could approve hidden/no-JS source and tampered historical Margins; image screenshots could race decoding | Exact published evidence and 7-width/first-screen/no-JS fail-closed review | New helper 6/6 local tests PASS; full WordPress/browser NOT RUN | Homepage engineering + independent QA |
| Contextual actual paid FV product (not yet verified) | Confirmed lead → reviewed merchant offer → paid order | No seller-confirmed relevant rights-cleared SKU, order/refund/fee ledger or campaign denominator | **No offer activation or tracking**. Claude #820 must verify commercial truth | NET REVENUE / 1k qualified humans: UNKNOWN, not zero | Claude commerce/analytics; founder approvals |
| Grok source asset | Video CTA → relevant article/homepage → Focus | Exact Grok published asset IDs and attribution not supplied to this lane | No new UTMs/events, preserve TASK-008 queue | No visitor/sales claim | Grok/Praxxis |

## Gates still open
The serious unmodified Assembler desktop navigation-list axe finding remains HOLD until a real corrected full-document browser scan passes. Need actual anonymous WordPress/Assembler execution; true physical browser zoom, 320–1920 keyboard/touch/no-JS/axe, browser image HTTP bytes, Lighthouse/Core Web Vitals, licensed historical media, founder visual inspection, independently signed QD and exact-head CI. WordPress.com Personal has **no native staging clone**; isolated Playground is not hosted Atomic/Jetpack parity. No production CMS, nav, settings, theme, signups, subscribers or user records, posts, email, merchants, analytics, social content, or spending altered by this draft.
