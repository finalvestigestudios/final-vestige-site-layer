# R486 QA and governance receipt — 18 Nov 2026 PT

**Scope:** isolated Mind r486 source only. **Publication/commerce status:** HARD HOLD. **Evidence checkpoint commit tested:** `0383f203878a57f3041028b5c6805b12938eba99`. The QA receipt itself was committed *after* tests; pre-receipt content files are unchanged by adding this receipt.

## Executed code/source checks — exact connected-GitHub fetches

The eight committed source paths were fetched from the named branch using authenticated GitHub fetch_file; the complete committed `QA_TESTS.test.cjs` was executed under V8 using a minimal compatibility shim for built-in `node:test`, `node:assert/strict`, `node:fs` and `node:path`, backed by the exact fetched GitHub source blobs.

**14/14 portable assertions PASS** under that compatibility runner:

1. Identical substantive buying core in variants A and B.
2. B-only original SVG storyboard; no playable or embedded remote video.
3. Natively disabled purchase control on both pages.
4. No clickable Inspire3/Zen12 merchant href on either page.
5. No JavaScript, form, iframe or remote resource request in buyer variants.
6. FTC relationship disclosure adjacent to disabled merchant CTA.
7. Existing free Focus route present as real link.
8. Seller's formats and limits; bundle differentiation.
9. Six exact 7-second VTT cues totaling 42 seconds.
10. Original film transcript includes six timed sections.
11. New feature is over 1,800 words and includes original/counterevidence.
12. Four distinct Mind hub streams and verified FV site links.
13. Claim/release matrix holds missing commercial permission and rejects unsupported equivalence.
14. No fabricated paid conversion, published creator IDs or revenue; basic no-JS/a11y semantics.

An **additional 15/15 direct source-blob checks PASS**, covering buyer-core equality, disclosure proximity, links, formats, study boundaries, the hub and documented unknown revenue.

**6/6 synthetic unsafe modifications detected** in memory: removal of native disabled state; deletion of disclosure; inserted clickable merchant href; missing optional film; damaged caption duration; forged activated earning URL. No unsafe mutation was committed.

**Limit:** This runner executed the source test functions with V8-compatible built-ins, not the real Node.js test runner. A real native command is prescribed but **was not executed**: `node --test mind/r486/QA_TESTS.test.cjs`. GitHub or staging review should run the native command against the final exact SHA before release.

## Original files in this branch

- `THE_WHITE_BEAR_THAT_WOULD_NOT_LEAVE.md`: ~2,036 original words, directly links 1987 white-bear experiment, 1993 failed-rebound report, 2020 31-study analysis, ethical Puységur archival bridge and free neutral observation exercise.
- `ZEN12_A_TEXT_ONLY.html`: complete independent full buyer guide, accessible static HTML, no scripts or merchant links.
- `ZEN12_B_OPTIONAL_42S_STORYBOARD.html`: exactly same buyer core plus original SVG poster, optional 42-second transcript concept; no encoded/hosted film, no autoplay or A/B result.
- `ZEN12_OPTIONAL_42S_CAPTIONS.vtt`: 6 caption intervals.
- `MIND_HUB_SOURCE_ONLY_GUTENBERG.html`: standalone four-stream scoped Gutenberg source candidate; no CMS draft/save performed.
- `CLAIMS_SOURCES_PERMISSIONS_AND_RELEASE_GATES.json`: 25 claim decisions, 14 source URLs, 30 gates.
- `OFFER_FUNNEL_CREATOR_CROSSWALK_AND_REVENUE_ACCEPTANCE.md`: offer-first blocker plan, 3 source-matched creator topics, first-party measurement contract and paid A/B hypothesis.
- `QA_TESTS.test.cjs`: portable 14-test regression suite.
- This receipt.

## Unexecuted, mandatory before any release

- Native Node run and independent CI on exact final source.
- Real-browser tests at 360, 390, 768, 1440 and 1920 px; keyboard, focus, 200% zoom, screenreader, reduced motion, captions, no-JS and no-play tests.
- WordPress Gutenberg sanitizer and theme CSS isolation/staging preview. Current hub is source text only, **not** a WordPress CMS draft.
- No copyediting/legal rights report or product-specific independent clinical trial proof; cannot copy seller health/wealth promises.
- Actual encoded/original 42s media has **not** been created or hosted in this branch.
- Existing Jetpack confirmed signup/welcome delivery not executed, and no test subscriber registered.
- No merchant acceptance, earning URL, web/email channel rights, eligible SKU final checkout/returns, order, settled commission or purchase.
- Real Grok IDs/post URLs and end-to-end attributable qualified-human cohort are missing; all 7/30-day net revenue rates remain **NOT COMPUTABLE**.
- No live A/B visitor randomization, commercial CTA or traffic experiment performed.

## Seller-specific compliance distinction

Read https://inspire3.com/ , https://zen12.com/about , https://zen12.com/ and https://zen12.com/secret/ on 18 Nov 2026 PT. The standard packages and coupon-led funnel differ. Official descriptions of session lengths, formats, levels and advertised guarantees are attributed to seller and are not product-specific efficacy proof, stable offer prices or FV partner authority. The public seller sites are cited in plaintext in the guide rather than live merchant links.

FTC reference: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance . Material relationship must be clear near a future specific earning link; unsubstantiated clinical outcomes, personal experiences, guaranteed earnings and artificial urgency remain disallowed.

## Release governance

- **Protected:** homepage flagship PR #49, agent homepage Issue #150, canonical Mind hub PR #172, Dispatch Issue #174 and its Jetpack welcome; all unchanged by this additive branch.
- **Not performed:** CMS or navigation edit, mail send, social post, paid tools, partner activation, tracking pixel, deploy, PR merge or founder-release action.
- **Owners:** Founder/Commerce — merchant credentials/eligibility and paid SKU; Claude — existing first-party analytics and checkout audit; Site QA — browser, WordPress sanitizer and security; Praxxis/Grok — three genuine social IDs and approved links; Mind — independent writing, source checks and presell; Founder — all production/commercial approvals.

The test result establishes **static source controls, not customer or commercial success**. Prioritize authenticated payable offer and refunded-net revenue ahead of page volume.
