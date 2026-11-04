# Dispatch R123 — Focus gift-display truth, duplicate-signup friction, and commercial release evidence

**2026-11-04, 14:36–14:50 Pacific. DRAFT / UNSENT / NO LIVE CHANGES.**
Canonical original campaign: PR #175, exact head d57ccdba3aee8f065e143e101c2945f4f3d01647; readiness PR #201; immediate parent PR #994. Issue owners: Dispatch #174, Focus #129, Mind & Affiliate #171, conversion #820; Grok/Praxxis TASK-008 remains separate. Homepage PR #49 untouched.

## Newly observed source-level problem

Authenticated WordPress read of the published Focus page (ID 1579; https://finalvestige.com/focus/) gives a short inline script identified as fvf-gift-v2. It reads the subscribe query parameter and reveals the free Fieldbook panel if that value is nonempty and not one of five known error values:

    var bad=['invalid_email','error','blocked_email','opted_out','blocked'];
    var q=null;try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){}
    if(q){if(bad.indexOf(q)<0){show();}}

It also shows the panel when the subscriptions container gains a CSS class named is-subscriber. Crucially, the actual WordPress regex uses **word boundaries**, not a DOMTokenList class containment check; it can match a synthetic class such as not-is-subscriber as well. The accompanying simulator deliberately reproduces this loose word-boundary behavior, so no UI class string qualifies as authenticated consent. This is an **on-page reveal**, not an authenticated event that a specific person gave consent and confirmed the WordPress email. Any novel query value, including subscribe=foo, subscribe=thanks, and subscribe=confirmed, reveals the panel in the observed script logic. A copy/pasted URL alone can produce it. The PDF link is already in public page markup; this does not expose a private document or subscriber address.

The existing Focus FAQ says **"Tap the download button after you confirm your email"**. That implies a confirmation gate for the button, but the source-level reveal does not enforce it. The mobile FAQ also instructs users to open in Safari or Chrome **"and sign up again."** That could cause duplicate signup attempts, inflate signup-click diagnostics, and frustrate already-confirmed subscribers. The gift panel itself correctly says **"Please confirm your email to join The Dispatch."**

These are **source-observed** findings, not proven browser reproductions. A Gutenberg Subscribe block is serialized as a fallback link in the WordPress content response; its actual on-page hydrated/form behavior must be checked in a genuine browser before anyone calls the form broken. No user signup was submitted during this investigation.

## Source-level truth table (synthetic; no signup requests)
| Controlled input | Gift visible under observed JS? | Proof of new confirmed subscriber? |
|---|---|---|
| subscribe=foo | Yes | NO |
| subscribe=success | Yes | NO |
| subscribe=confirmed | Yes | NO |
| subscribe=error | No (absent subscriber CSS class) | NO |
| subscribe=blocked | No (absent subscriber CSS class) | NO |
| is-subscriber class | Yes | NO new consent-event proof |
| Reader downloads existing public PDF | Irrelevant | NO |
| Connected inbox contains WordPress confirmation request | Irrelevant | NO confirmation clicked proof |
| Native authenticated confirmation + consent proof | Not dependent on gift | Eligible for independently deduplicated event |
| Imported in last 24 hours rises | Irrelevant | NO |

The accompanying CommonJS source guard is deliberately incapable of subscribing, sending, tracking, or rewriting WordPress. It labels any client-only signal diagnostic and returns no paid orders or customers.

## Exact proposed Focus FAQ replacement (NOT deployed)
Replace the statement that confirmation gates the download with:

> **I requested the Fieldbook. How do I join The Dispatch?** Check your inbox for the subscription confirmation message and follow its link to join. The Fieldbook download button may appear on this page before you confirm your email; downloading the PDF does not confirm your subscription. The welcome email is configured to contain the same PDF link once you confirm.

Replace the instruction to sign up again on mobile with:

> **My phone will not open the PDF. Do I need to sign up again?** No. Open the PDF link you already have in Safari or Chrome, or use the link in your welcome email if it arrives. If you haven't confirmed your subscription, check for the confirmation email first. You don't need to enter your address again.

No new urgency, medical claim, hidden signup, lead magnet, or outbound affiliate link is introduced.

## Verified native WordPress snapshot (read-only, 2026-11-04 22:38:32–35 UTC)

- Newsletter enabled, site_can_send true, automatic new-post mail **off**, email_content_format excerpt, from name Final Vestige, reply-to no-reply.
- Subscriber totals **3 total / 3 confirmed / 2 unconfirmed**, suppressed 0, imported_last_24h 1. These categories are not additive. Import activity is not proof of new consent or an independently email-reachable audience.
- Five recent post notifications are **never_sent_opted_out** (flag false), with zero dispatch timestamps in diagnostics. No actual mail was sent in this sprint.
- Welcome message currently points to the existing Complete Edition PDF described as 52 pages; it does not prove the file opened or that an inbox received it.
- Narrow connected Gmail searches found an October 25 request to confirm a WordPress subscription but did NOT find a completed Fieldbook welcome or named FV-specific Inspire3 approval in the searched results. Do not conclude the messages never existed elsewhere; do not publish addresses.

## Precise conversion instrumentation contract (proposal, Claude owns production)

**One event name: confirmed_signup.** Emit only from an authenticated, consent-supported native WordPress confirmation event, after server-side pseudonymous deduplication. Use a secret-keyed HMAC of the native subscriber identifier and a stable native event ID; never expose raw email, subscriber identifiers, confirmation URLs, verification tokens, browser fingerprint or IP in the client or GitHub. Reject replay/reconfirmation as a new lead. For already-confirmed subscribers retrieving the Fieldbook, do not increment lead count.

Client-side only diagnostics may be named focus_signup_click, focus_gift_revealed, focus_pdf_click, and focus_email_confirmation_instructions_viewed. Those are neither leads nor purchase conversions. Retain Grok asset_id and permitted UTM attribution only when genuinely associated with a consented, authenticated lead; do not infer source from aggregate count changes. No new tracking pixel or duplicate measurement script; Claude integrates with existing analytics if approved.

Do not treat confirmed status alone as reachability. Native eligibility, suppression, bounce handling, and welcome receipt are separate proof objects. Neither a successful publisher preview nor a configured welcome proves inbox delivery.

## Conversion-first decision table

| Offer → funnel step | Blocker | Change/experiment | Current result | Owner |
|---|---|---|---|---|
| Fieldbook → confirmed lead | Free-PDF visibility conflated with email confirmation | Separate client diagnostics from authenticated server confirmed_signup, dedup | Source risk VERIFIED; actual event flow NOT TESTED | Dispatch (contract), Claude (implementation) |
| Fieldbook → completed download | Contradictory FAQ and duplicate signup advice | Review two replacement FAQ paragraphs; independent mobile QA | Copy BUILT, not live | Dispatch/Claude |
| Dispatch → legitimate recipient | Native subscriber reachability unknown | Read-only private status and consent reconciliation | NOT VERIFIED | Dispatch/Claude |
| Welcome → reader | 52-page PDF configured, receipt and actual pages not independently inspected | Authorized inbox plus PDF review without sending unauthorized email | NOT VERIFIED | Dispatch/Site QA |
| Editorial Issue01/02/04/06 → article | Jetpack excerpt/subj/footer actual transport not seen | Native preview and compliant rendered email under approved testing | Static MIME prior tests only, NOT RECEIVED | Dispatch |
| Issue03 Zen12 → guide → merchant | No named FV email permission, guide not live, no authoritative terms/settlement | Mind #171 supplies written permission and live independently vetted guide first | HOLD_MERCHANT | Mind Studio |
| Issue05 Total Focus → guide → merchant | Same rights/guide unknown; seller's efficacy not independent evidence | Maintain hold pending separately reviewed qualification | HOLD_MERCHANT | Mind Studio |
| Grok asset → paid customer | Qualified human sessions and independently settled transactions missing | Reconcile permitted UTM asset ID, confirmed orders, refunds and fees | NET REVENUE/1,000 NOT COMPUTABLE | Praxxis/Claude |

## Merchant and FTC checks, 2026-11-04

Zen12 official source https://zen12.com/hnp describes audio product formats and makes claims about achieving an hour's meditation benefit in 12 minutes; this is a *seller* claim, not substantiated product-specific equivalence. Official Total Focus https://hypnosislive.com/mental-skills/total-focus lists a 33-minute 47 MB recording, displays a standalone price alongside a discount/bundle, and advertises a 14-day refund. The terms actually applicable at purchase, refund handling, approved link format, named affiliate approval and permission to promote via newsletter are UNKNOWN. The public portal https://affiliates.inspire3.com/ does not demonstrate FV acceptance.

Under FTC guidance https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business, commercial messages require truthful sender/subject, conspicuous ad identification as applicable, a valid **Final Vestige publisher** physical postal address, and a usable opt-out method. Automattic's address in a past confirmation is not a substitute. No actual Jetpack commercial footer or opt-out receipt has been verified. Commercial disclosure must be near qualifying offers; sitewide disclosure alone is insufficient.

## Required verification before any production release

1. Claude reviews and fixes the two proposed FAQ sentences if approved, preserves one Jetpack list, and confirms the actual rendered Subscribe block with no network POST.
2. Independent read-only browser QA exercises query variants and returning-subscriber states across mobile 320/390 and desktop, with keyboard and no-JS fallbacks. Observe DOM only; do not submit real emails.
3. Audit existing analytics for wrongly named confirmed_signup events from URL query, success display, PDF click, CSS class, or subscriber count delta; change only under Claude's existing production governance.
4. Validate authoritative **private** WordPress confirmation/eligibility/welcome receipts with appropriately authorized test procedure, without contacting subscribers or importing any addresses.
5. Founder gives explicit, separate final approval of manuscripts, recipient eligibility, commercial rights, footer, preview, send mechanism and cadence. Until then all six HOLD_UNSENT, commercial #03/#05 HOLD_MERCHANT.

**Neither a UX correction nor a synthetic test is a paid sale.** Definitive north-star KPI is realized net revenue per 1,000 qualified human sessions (7/30-day cohorts), requiring independently reconciled paid orders net of fees/refunds. No values available in this sprint.
