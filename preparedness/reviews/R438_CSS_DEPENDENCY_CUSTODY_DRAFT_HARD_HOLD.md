# R438 Preparedness — CSS dependency and visibility custody (DRAFT / HARD HOLD)

Owner: Preparedness Archive integration #136, revenue decision #820. Not the website, Grok, Praxxis, commerce, or independent QD owner.

## Problem reproduced (synthetic, not a live exploit)

R437's no-JS/print gate correctly identifies linked print stylesheets, but the same valid and byte-identical **screen-only** `<link rel="stylesheet" media="screen" ...>` can contain CSS altering warning visibility without the R437 pair checker raising a structural error. An identical `<style>@import "/theme.css" screen;</style>` also passes R437 because the @import's actual bytes are not in the HTML. These are reproducible **review gaps**, not evidence of malicious production content.

## Additive read-only gate

- Inventory and SHA-256 fingerprint **all** embedded stylesheets, inline element styles, stylesheet links, preload styles, linked SRI/crossorigin/media attributes, `<base>` link-resolution controls, and hidden/inert/ARIA visibility switches across proposed WordPress and private-preview HTML.
- Reject / escalate CSS `@import`, `url()`, external linked stylesheets including screen-only, unsafe CSS-link schemes, escaped tokens, generated `content:`, potential warning concealment via styles, print contexts, bidirectional/zero-width controls and malformed style structure.
- Detect per-export presentation/asset-provenance drift without silently rewriting or normalizing dissimilar documents. Preserve all upstream source/citation and reading-depth checks by composing R437.
- Fail closed on missing original manifest/lock/exports or unavailable parent. Every output remains DRAFT_HARD_HOLD, publication/safety/commerce approval false, no claimed merchant sale or net-revenue KPI.
- This parser is conservative. A stylesheet reference is **not automatically unsafe**; it is unauthenticated by this isolated evidence packet. A real browser/print/screen-reader test, asset-byte lock, qualified reviewer and provenance adjudication are still required.

## Local execution / evidence

- 66/66 new deterministic unittest methods PASS, 448/448 combined R430–R438 local synthetic unit tests PASS after reconstructing earlier exact source/test modules from evidence bundles and placing the original R434 parent in its expected module directory. Initial assembled combined replay failed (43 failures/4 errors) **only because the R434 parent module had not yet been placed**; after restoring that parent, the final 448/448 run passed. The 66/66 new test suite was independently green both before and after.
- Python compilation PASS. Missing-original-evidence CLI returns exit 2 with DRAFT_HARD_HOLD.
- The local tests are synthetic, not native 35-article `validate.py` / `build.py`, 70 authentic paired WordPress/private-preview exports, real browser-based computed-style or independent QD review.
- No original content, URLs, source IDs, source-use evidence, safety statuses or branch heads have been changed.

## Source and cross-agent HOLD register

Original ledger: 35 articles, 203 unique source IDs, 280 source appearances, 17 exact shared-URL groups, 5 unresolved source-applicability disputes, 9 original manuscript forks. Nine original Claude/Shelter branch refs are PINNED/IDENTICAL (zero ahead or behind) as of this run. QA PR #157 HEAD 7d1ae6b8ef93d10cfb6810987672360885e9c1aa; synthetic PR #169 HEAD e9cd7766dac59d47ab467d8945269b9146c2aef5; dependent repair #2205 HEAD bbcf1859768624c611df4abadc564c18247cf32a; homepage #1689 HEAD f55c36b6598eec558dd8bb24e4c8988becc51be0. All untouched.

Additional editorial severity: Article #11 original jerky composite needs process-level qualified review (E428–E430). Historical-source provenance is not food safety permission. Article #7 water and Article #15/Tool #104 child-contact privacy/emergency scope remain held.

## Founder commerce priority: OFFER → FUNNEL STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER

| Offer / path | Funnel step | Blocker | Safe proposed next action | Evidence | Owner |
|---|---|---|---|---|---|
| **ONE authenticated FV-owned Preparedness practical pack** | Free official guide → optional paid purchase | No verified FV seller rights, sale-ready SKU/checkout price, lawful delivery, refund promise or merchant receipts | Authenticate real currently payable product, full rights and fulfillment **before enabling any paid CTA** | HARD HOLD; no paid-conversion claim | Founder/Commerce |
| Already-published *family emergency contact/reunion* creator asset | Grok social asset_id → free current resources | No verified relevant published asset_id, rights, post URL, mobile landing, allowed UTM | Grok/Praxxis independently match one already-published post to `https://finalvestige.com/preparedness/` (not unreleased Article #15) | UNMATCHED, no attributed sessions | Grok/Praxxis |
| Free Archive → optional family contact wallet card Tool #104 | Guide → clearly labeled voluntary download | Tool #102/#104 identity; Article #15/local emergency wording; child privacy, print and JS-off QD unresolved | Keep draft. Qualified emergency/privacy and real device/print review | HARD HOLD | Preparedness/QD |
| Verified sale → realized net revenue | qualified-human 7/30d visits → CTA → confirmed lead → settled order less fees/refunds | Merchant/consent/cohort source evidence missing; avoid scripts | Coordinate measurement schema with Claude, no duplicate scripts, no claiming clicks as sales | NOT COMPUTABLE | Claude/Commerce |

Draft CTA remains **"Review the official household emergency checklist."** This is a source-backed free agency-resource path, not a validated commercial funnel. The retired water freebies and unrelated merchant products remain excluded. #820 takes business release priority but cannot override #136 safety/QD gates.

No merge, release, public publishing, CMS/navigation write, social content production/posting/queue edit, email send, analytics deployment, merchant/affiliate activation or spending.
