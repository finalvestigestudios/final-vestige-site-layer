# Dispatch R134: Native master-suite verification + conversion truth bridge (UNSENT)

Parent: PR #1064 at `f0d885da32ab33e32a1ffe461386cd25f18a0608`; master PR #175 at `d57ccdba3aee8f065e143e101c2945f4f3d01647`. Evidence: GitHub Issue #174; coordination #171, #129, #820. Existing six messages and 4-editorial/2-commercial allocation are unchanged. This branch is draft-only. Homepage PR #49 remains frozen.

## First-time native execution of the original master tests

Retrieved the **exact eight input files** from the GitHub master PR #175 head: test_campaign.py, manifest.json, and six .md issues. Independently verified local `git hash-object` SHA-1 blob values match the returned GitHub blob SHA for **all eight** files:

- tests/test_campaign.py: `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`
- manifest.json: `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`
- 01: `039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8`
- 02: `faa207ab7deafd86460d36f8c17fe62d392d0e14`
- 03: `aeeef34efea0cc281f69901488e4501fea851245`
- 04: `89635bfb9c8d1ff17297a59b6b5b5b2a176934ca`
- 05: `a9dfaa450ba025a7b5113ade8a294d6dbad778dc`
- 06: `004d558df6376d2ad6f4f79a4581e8d2c444e355`

Executed native Python 3.13.5: `python -m unittest discover -s tests -p 'test_*.py' -v` → **6/6 PASS**. This resolves the longstanding missing original Python execution, though it is an exact reconstruction in a local directory rather than a Git checkout and does **not** verify hosted CI or Jetpack. The original manuscripts remain UNSENT.

## Newly observed conversion blocker candidate: /dispatch/ sign-up control

Authenticated WordPress `pages_get(slug=dispatch)` returned published page #523 with a `wp-block-jetpack-subscriptions` element whose serialized inner HTML shows a **Subscribe anchor linking back to the same page**, not an email input. This is API source evidence, **NOT** proof of a public signup malfunction. WordPress can render dynamic signup controls differently per viewer. An attempt to read the public page through web-fetch failed. Prioritize **signed-out visitor DOM/browser inspection without submitting any personal data**, including button behavior, keyboard navigation, accessible label and /focus/ consistency. Claude owns changes; Site QA should independently confirm. Do not rewrite/replace the native Jetpack form without that evidence.

## Authenticated WordPress status (2026-11-05T09:39Z)

- subscriptions=true, site_can_send=true; email_new_posts_by_default=false; email_content_format=excerpt; reply_to=no-reply; welcome message still contains the official 52-page Focus Fieldbook PDF URL.
- total=3, confirmed=3, unconfirmed=2, suppressed=0. Categories are **not additive**; actual current email-eligible recipients unknown until private `Email subscription: Subscribed` filtering.
- Five recently published posts returned `never_sent_opted_out` and `dispatched_at=null`; zero evidence of recent sends.
- Actual received Fieldbook welcome, native email preview, full footer, functional unsubscribe, merchant email permissions and real paid orders remain **NOT VERIFIED**.

`snapshot.json` records only these anonymous aggregates, explicit unknowns and source limitations. `journey_gate.py` fails closed against false confirmed signups, missing subscriber provenance, unverifiable delivery, undeclared merchant permission, fabricated paid orders and invalid revenue denominators. Its evaluated release state always remains HOLD_UNSENT, even in synthetic all-green conditions. `test_journey_gate.py` has **16/16 native Python tests PASS** including adversarial cases and synthetic-only arithmetic. No subscriber identities, emails, API keys or private checkout identifiers are stored.

## Original, optional precise-SKU issue 05

`issue05-total-focus-optional.txt` and `.html` are matching plain-text/email-safe render candidates discussing **Hypnosis Live Total Focus**, not the seller's different **Hypnotize Yourself** recording. No active earning link or live buyer guide is represented. One guide CTA deliberately remains disabled and the prospective commission disclosure appears beside it. A practical free exercise, source URLs, seller/independent claim distinctions, price volatility, refund caveats, and explicit postal/unsubscribe blockers are included. These are editorial alternatives, **not** approved replacements or actual Jetpack messages. The independent exact-SKU guide is in Mind Studio draft PR #1066 and is NOT live.

`review.html` is an accessible offline review board, no analytics or PII. Offline Chromium rendered the review and optional email HTML at **320, 390, 768, 1440px** (eight checks, zero observed horizontal overflows). These screenshots and tests are available in the associated local QA package; Chromium's initial file:// navigation was blocked by the runtime and the final passing checks used page.set_content, **not** public-web or inbox delivery.

## Specific official sources and restraint

- Zen12 seller: https://zen12.com/hnp — twelve levels, four styles, 48 MP3s are seller-listed specs. The hour-in-twelve-minutes effectiveness promise is **not independently proven** here.
- Total Focus seller: https://hypnosislive.com/mental-skills/total-focus — 33 minutes / 47 MB; $24.44 displayed on November 5 but no verified checkout, avoid freezing a price.
- Refund limitations: https://hypnosislive.com/faq
- Public affiliate portal: https://affiliates.inspire3.com/ — existence of a program does **not** verify Final Vestige acceptance, allowed email promotion or tracking links.
- WP subscriber statuses (updated Nov 4): https://wordpress.com/support/subscribers/
- WP Subscribe block: https://wordpress.com/support/wordpress-editor/blocks/subscribe-block/
- FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Final Vestige live editorial standards: https://finalvestige.com/editorial-standards/
- Social handoff TASK-008: https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit

## Offer → funnel → blocker → change / experiment → evidence → owner

| Offer / stage | Blocker | Next check | Evidence now | Owner |
|---|---|---|---|---|
| Fieldbook → confirmed lead | Visitor form state and native consent not verified | Signed-out browser DOM + private native status filter; no unapproved submit | Source-only HTML anchor; NOT VERIFIED visitor behavior | Claude / Site QA / Dispatch |
| Dispatch → landing CTA | Excerpt truncation modeled for all six original CTAs; real render unknown | Non-sending native preview, later *separately approved* inbox test, footer and legal address check | NOT TESTED live | Dispatch / Claude |
| Zen12 guide → paid buyer | Named acceptance, specific email rights, live guide absent | Partner records, link/consent permission and exact buyer guide | HOLD_MERCHANT | Mind Studio |
| Total Focus guide → paid buyer | Buyer guide draft, source terms and affiliate rights uncertain | Align exact SKU/guide/link; verify price at actual checkout | Draft PR #1066 only | Mind Studio |
| Grok asset → revenue | Qualified visits, settled orders/fees/refunds unavailable | Source asset UTMs → confirmed lead → independent paid reconciliation | Revenue/1k qualified sessions NOT COMPUTABLE | Praxxis / Claude / Growth |

**Release decision:** all six HOLD_UNSENT; commercial issues 03/05 additional HOLD_MERCHANT. No email, test email, list export, WordPress content/settings change, affiliate activation, social posting, paid service or revenue claim in this sprint. Founder retains final approval of any sending, content publication and commercial activation.
