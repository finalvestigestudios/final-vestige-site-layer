# R286 — Focus Consent Truth Boundary & Editorial Close
**November 11, 2026. REVIEW ONLY. No sends, publication, subscriber changes or merchant activation.** Linked to Issue #174, master original #175, independent release preflight #201 and source-owner #171. Stacked on Dispatch PR #2076; homepage PR #49 untouched.

## Verified Focus client-side weakness
On authenticated read-only WordPress /focus/ page #1579, modified November 5, the live inline script 'fvf-gift-v2' reads `new URLSearchParams(window.location.search).get('subscribe')` and reveals the gift element for **any nonempty value** except five rejected statuses (invalid_email, error, blocked_email, opted_out, blocked). Thus an unrecognized `?subscribe=unknown_state` may reveal the gift panel. Jetpack's `is-subscriber` CSS class also reveals the panel. **This establishes a client presentation trust-boundary issue, not an actual consent bypass, fake subscription, sent email, or receipt.** UI, URL, CSS, and PDF retrieval must never emit confirmed_signup.

## Implementable, not-deployed engineering handoff
1. Claude/Focus should remove broad query-success inference or constrain the UI to verified states; even a visually successful state is **not** subscriber authentication.
2. Count `confirmed_signup` once per **authenticated provider-confirmed and currently email-permitted lifecycle**, with durable de-duplication; opt-outs, suppression and reactivation rules must be reconciled with the actual provider.
3. No recipient PII, email, phone, IP, raw subscription IDs or hashes in campaign URLs/analytics/GitHub. This repo's `focus_consent_contract.mjs` is a **pure offline prototype**, not a production collector or API integration. Its in-memory Set is a test stand-in, not production persistence.
4. Count independently authenticated paid orders or settled merchant commissions net of refunds and fees, not CTA clicks, PDF views, follower counts or confirmation requests.
5. No new tracking script. Coordinate event implementation with Claude, whose production analytics work takes precedence.

## Issue 06 review alternative
Subject: **The detail you missed was there all along**. Preheader: **An experiment from 1997, a seven-day question, and a better way to examine what you notice.** One first-party CTA leads to the published [Change Blindness report](https://finalvestige.com/2026/11/02/change-blindness/), avoiding original Issue 06's repeated Fieldbook CTA after welcome. It distinguishes the actual 1997 Rensink/O'Regan/Clark experiment and 1999 Simons/Chabris study from promises of self-improvement. Research sources: [1997 APS](https://www.psychologicalscience.org/journals/psychological-science/j.1467-9280.1997.tb00427.x/) and [1999 NLM](https://pubmed.ncbi.nlm.nih.gov/10694957/). Static HTML and synchronized plaintext reviewer assets are **NOT ADOPTED** and deliberately contain unsub/address hard-stop placeholders.

## OFFER → FUNNEL → BLOCKER → NEXT CHANGE/TEST → EVIDENCE → OWNER
| Offer | Funnel | Blocker | Test/change | Evidence | Owner |
|---|---|---|---|---|---|
| Zen12 | subscriber→vetted presell | FV-specific email affiliate permission, valid earning URL, actual live buyer guide absent | authenticate account, channel rights, page and offer-specific claims | **HOLD_MERCHANT**; public SKU page ≠ authorization | Mind Studio |
| Fieldbook | visitor→confirmed lead | query-driven gift appearance ≠ provider consent; diagnostic subscriber counters inconsistent | server/provider-confirmed subscription + privacy-safe de-dup | **UNKNOWN eligible audience** | Claude/Focus |
| Dispatch | consented lead→mailbox | publisher address, unsubscribe, true email rendering & welcome receipt unverified | official WordPress **Preview email** with per-post sending off; actual delivered-email test only after separate approval | **HOLD** | Dispatch |
| Grok content | human sessions→landing | asset-level/paid-sale linkage incomplete | use real published asset_id with existing attribution, never new pixel | **NOT VERIFIED** | Grok/Praxxis/Claude |
| Merchant | click→settled sale | no verified paid transaction / fees / refunds | reconcile authenticated merchant settlement and 7/30 day qualified cohorts | **NET PER 1K NOT COMPUTABLE** | Commerce |

## Current source-of-truth
Authenticated Jetpack Newsletter 2026-11-11 18:33 UTC: enabled, automatic new-post email **off**, full email format, 52-page Fieldbook welcome configured. Diagnostic **total3/confirmed3/unconfirmed2** and separate **WP.com Reader followers3/email followers0**; these are **not additive**; real eligible recipient count **UNKNOWN**. Five inspected posts each `never_sent_opted_out`. WordPress reports site_can_send=true; does not mean permission to send. Actual received welcome and unsub/footer not verified.

Original six-issue 4-editorial/2-commercial manifest and all manuscripts remain unchanged. Commercial 03/05 remain unapproved. Editorial/footer classification under FTC must assess actual primary purpose; only genuine Final Vestige postal address and functional unsubscribe in rendered message can satisfy release QA. No publisher/account-specific Inspire3 EMAIL permission, authorized merchant link, current terms or settled commissions were proved.

**OFFLINE QA:** local native Node `node --test test_focus_consent_contract.mjs` 28/28 pass; latest committed files must be read back independently. This module demonstrates synthetic truth-boundary behavior only. Browser, provider, WordPress preview, real inbox, native GitHub CI and paid order remain NOT TESTED / NOT VERIFIED.