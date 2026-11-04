# R112 | Dispatch truth-in-subscription and native transport release dossier
**Evidence captured:** 2026-11-04 11:31–11:32 UTC (connected WordPress/Jetpack; connected Gmail targeted read); public Zen12/Inspire3/FTC pages checked November 4, 2026. **Status: DRAFT / UNSENT / NOT LIVE.**

## Purpose; non-overlapping scope
**The business problem is trust and eventual paid conversion, not the number of email drafts.** A subscriber who is promised a research bulletin on every publication but receives no article email cannot reliably enter an evidence-led subscriber-to-customer journey. The website and welcome currently imply a direct publication-to-email connection. Jetpack's per-new-post default is **OFF**; the five observed post notifications were intentionally opted out. This is a **subscriber-expectation / copy-consistency risk**, *not proof of fraud, all-time zero sends, or email failure*: manual, explicitly opted-in posts might still be possible. The site must not switch to automatic sends to fix a copy problem.

This package is an **independent, pure, no-network audit** of the existing native platform configuration, canonical source CTA routes and draft-language alignment. It adds **NO** newsletter platform, signup list, script to production, merchant link, paid vendor, subscriber identifier, send code, live WP change, or changes to Grok, Claude, homepage PR #49, Mind Studio, or the original six manuscripts.

**Source lineage:** original master draft PR #175 at `d57ccdba3aee8f065e143e101c2945f4f3d01647`; existing readiness PR #201 at `ef53e5a17046e3dff5a4a7e3b0f4c8fbce9cd6f6`; immediate parent R111 draft PR #926 at `087f39c5a9ab496a3ae41f597dfb309d9559c1cc`. This R112 branch is stacked *on #926*, not main; its diff must not be represented as an independent mainline landing. All six master issues untouched.

## What was actually observed
Read-only connected WordPress `newsletter.status` at `2026-11-04T11:31:36Z`: `site_can_send=true`, total=2, confirmed=2, unconfirmed=2, suppressed=0, latest 5 all `never_sent_opted_out`, with no recipient/sent counts. `newsletter.get_settings` at `2026-11-04T11:31:39Z`: `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, `reply_to=no-reply`, `from_name=Final Vestige`; the complete Fieldbook PDF URL is **configured** in the welcome message, not verified as received or downloaded. Native follower summary previously reports 2 WordPress.com/Reader and 0 email followers; this must be kept separate, not combined with 2 confirmed and 2 unconfirmed. Official WordPress semantics exclude unconfirmed from total.

Connected site content (READ ONLY):
- Published `/dispatch/` page ID 523: “New investigations and archive finds by email, when we publish them”; “You'll also get new investigations … when we publish them”; “Your welcome email includes … 52-page workbook”; has a Jetpack subscribe block and privacy/unsubscribe line. **Does not** contain equivalent prospective affiliate-recommendations disclosure.
- Published `/focus/` page ID 1579: native Jetpack signup; contains commission-recommendation language; Fieldbook content linked. It is not a paid offer.
- Published `/editorial-standards/`: archival/primary evidence priority, no conflation of inference and fact, disclose commercial relationships, source corrections.
- Published editorial CTAs verified by connected WP source for issue 01 `/the-missing-caption/` page ID 1122; issue 02 `/free-resources/puysegurs-animal-magnetism-files/` page ID 1377; issue 04 `/2026/08/20/the-hatch-opened-inward-apollo-1/` post ID 434; issue 06 `/focus/` page ID 1579. **Published content metadata is not yet mobile click-through or page performance proof.**
- Commercial issue 03 and 05 guide CTAs still point to `[[...]]]` placeholders; DO NOT create a substitute or live affiliate URL in this branch.

Targeted connected Gmail read-only November 4:
- Search for an actual Fieldbook / “Welcome to The Dispatch” email since Oct 24: **none in the searched mailbox**.
- A WordPress subscription **confirmation**, October 25, was found; it is not a welcome or proof of confirmed email eligibility.
- Targeted named Inspire3/Zen12/Hypnosis Live affiliate-approval, email-permission, and link searches: no qualifying acceptance message found. The account may have other evidence elsewhere; these searches do *not* prove there is no approved affiliate account.

## Hard-hitting CTA/revenue review
1. **Highest-intent offer: NOT YET VERIFIED.** The closest editorially relevant paid candidate remains Zen12; it is not an eligible Final Vestige email promotion until written account acceptance, product approval, lawful email channel permissions, link rules, purchaser-data processing and independent merchant conversion reporting exist. A free Fieldbook download is a lead magnet, not a customer/order.
2. **Actual product source, not a catalog summary:** [official Zen12 package page](https://zen12.com/hnp) currently advertises 12-minute listening sessions and 12 levels / 48 MP3s for its Premium package. Its “one hour of meditation in 12 minutes,” automatic-brainwave and wellness-effectiveness representations are **seller assertions not established for this product**. The page displayed Premium **$87.99** on Nov 4; this is *NOT* a verified final checkout price/eligible affiliate price and MUST NOT appear as a fixed deal in pilot email. The seller describes a **one-year** refund guarantee; this is not independent refund outcome evidence and must not be confused with Hypnosis Live's different policy.
3. The [Inspire3 privacy policy](https://inspire3.com/privacy/) says buyer names, email and product-purchase details **may be shared with the referring affiliate**. FV's minimal-source revenue model must reject buyer PII and use aggregated/authorized merchant transaction reports when available.
4. **Email #05** must not inherit any Zen12 package/return claims; the separate Hypnosis Live *Total Focus* recording/claims and purchase terms need their own current seller-page and checkout evidence. It's a second *reserved* offer slot, not a second active campaign.
5. The current `email_content_format=excerpt` means an authorized publisher post would not necessarily deliver the six manuscript bodies, preheaders, near-offer disclosures and CTA. A static preview or locally generated HTML is **not a received Jetpack email**. Neither the editorial nor commercial issues qualify for a send on this evidence.
6. **CAN-SPAM** requires truthful headers/subjects, valid publisher postal address, conspicuous opt-out, and timely opt-out processing for commercial messages. Even a primarily editorial email can potentially be commercial depending on its subject and overall purpose; **do not assume four editorial slots are automatically exempt**. [FTC official guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business). The October 25 Automattic mailing address is **not** FV's publisher address.

## Proposed publisher copy ONLY (not approved / not deployed)
### A. /dispatch/ “what you'll receive” replacement candidate
> The Dispatch is our occasional research newsletter: original investigations, sources worth checking, and practical notes from the archive. Publishing an article on the website does not automatically email everyone. We send an edition only after we have reviewed it for readers. You'll also get the free 52-page Seven Day Focus Fieldbook in your welcome message, subject to your subscription being completed. Occasionally, a clearly identified product guide may contain links that earn Final Vestige a commission if you purchase. No purchase is necessary. Unsubscribe whenever you choose.

**Copy QA:** single list; no unsupported “weekly” delivery promise, no false claim the Fieldbook receipt was tested, no bait-and-switch, and an up-front commercial expectation. The draft must not say “we currently send weekly” when there is no proven send cadence. The term “get … in your welcome message” describes configured behavior, not proven deliverability; founder can choose softer “the welcome message is intended to include…” until delivery verified.

### B. Welcome message wording candidate (do NOT update)
> Welcome to The Dispatch. Here's the Seven Day Focus Fieldbook — Complete Edition (52 pages): [retain the **existing exact verified PDF URL**]. It is a practical notebook for a small attention routine, a seven-day record and careful questions about meditation-audio claims. You don't need to purchase anything. Final Vestige publishes new investigations on the site independently of our email cadence; selected Dispatch research editions are sent only when reviewed and approved. Some future editions may include an optional, clearly marked recommendation that could earn us a commission. We won't email a daily sales blast. You can unsubscribe through the link provided by WordPress. — Final Vestige Studios

**Important:** The email's actual final subject, From, List-Unsubscribe headers, HTML/plaintext rendering and address cannot be established by editing copy here. Preserve all current settings pending explicit founder final approval and authorized real received-mail QA.

### C. Source/CTA subject honesty rule
A subject or preheader can describe a mystery or evidence, but it must accurately match the **content actually received** under Jetpack excerpt mode and the linked article. Do not claim a draft Markdown preheader is a Jetpack native subject/preheader field; that integration remains UNVERIFIED.

## Six-edition route ledger
| Edition | Role | Destination | Native status | Release |
|---|---|---|---|---|
| 01: attention | Editorial | /the-missing-caption/ | Published page ID 1122 | HOLD_UNSENT |
| 02: Puységur | Editorial | /free-resources/puysegurs-animal-magnetism-files/ | Published page ID 1377 | HOLD_UNSENT |
| 03: 12-minute Zen12 | Commercial reserve | Approved Zen12 first-party warm-up guide | NO APPROVED LIVE GUIDE | HOLD_MERCHANT |
| 04: Apollo 1 | Editorial | /2026/08/20/the-hatch-opened-inward-apollo-1/ | Published post ID 434 | HOLD_UNSENT |
| 05: Total Focus | Commercial reserve | Approved separate Hypnosis Live first-party guide | NO APPROVED LIVE GUIDE | HOLD_MERCHANT |
| 06: attention log | Editorial | /focus/ | Published page ID 1579 | HOLD_UNSENT |

## Conversion-first prioritized contract
| Offer → funnel step | Blocker | Safe change / experiment | PASS/FAIL evidence | Owner |
|---|---|---|---|---|
| Free Fieldbook → confirmed lead | Current visit-to-confirmation transition and email eligibility unknown | Read-only private Jetpack Email Subscription status filter; correlate one native opt-in without exposing ID | Native new `confirmed_signup` once, no Reader-only inflation; **NOT YET PASSED** | Dispatch / Claude |
| Confirmed lead → promise fulfilled | Current copy implies automatic post news while default is off; welcome receipt not found | Review opt-in + welcome candidate above; inspect existing legitimately received MIME + download without sending | Received welcome and PDF, matching promise + effective opt-out **NOT YET PASSED** | Dispatch / Founder / QA |
| Dispatch email → chosen editorial article | Excerpt transport; native subject/preheader not verified | Offline exact-subject render, then authorized *received* Jetpack proof only after explicit approval | Native email content/CTA/footer verified **NOT YET PASSED** | Dispatch / Site QA |
| Subscriber → Zen12 evidence guide | Permission and live guide absent | Mind Studio's already drafted authorization request and eventual vetted guide; no activated link now | Written email right + published guide + exact link rules **NOT YET PASSED** | Mind Studio / Founder |
| Approved recommendation → paid order | No authenticated affiliate/FV-owned checkout and settlement | Independently reconcile merchant order, fees/refunds, no purchaser PII | Source-reported paid order/commission plus refund-adjusted amount **NOT YET PASSED** | Claude / Commerce |
| Grok asset → 7/30-day net revenue per 1,000 qualified humans | Source IDs and human sessions not independently reconciled | Existing TASK-008 and #820, standard utm_source/medium/campaign/content, no new analytics script | Verified asset_id→first-party session→paid order and denominators **NOT YET PASSED** | Grok / Praxxis / Claude |

**Metrics:** Report `confirmed_signup` only with authoritative native consent; email CTA clicks remain non-sales. No gross/net revenue, conversion rate, or KPI estimate is permissible without eligible human denominator, independent paid orders, fees and refunds. **Current result: NOT COMPUTABLE**, not zero. Small-cohort reports must suppress potentially identifying lead behavior (R111 existing threshold 20).

## Offline reproducibility and trust boundary
- `audit.mjs` contains zero network/process/browser/cookie/email/WordPress/write/send APIs. It reads explicit, sanitized input snapshots only.
- `test_audit.mjs` provides synthetic native Node test definitions for contradictory settings, disclosure parity, missing receipts, false attribution, route verification and activation drift. Tests are not proof of a live email.
- `native_snapshot_2026-11-04.json` has no subscriber addresses, personalized URLs, opt-out tokens, message identifiers or conversion inventions.
- `review.html` is an accessible no-JS human board with candidate copy. It is not a WordPress or inbox preview.
- Any test results must identify exact commit and execution substrate: local V8 harness ≠ native Node ≠ hosted CI ≠ browser ≠ received Jetpack message.
- No change to existing PR #175/#201 content, no drafts substituted without founder creative approval.

**Decision:** ALL SIX `HOLD_UNSENT`; commercial 03/05 `HOLD_MERCHANT`. No email/test send, WordPress write, list import, affiliate activation, Grok task edit, or spend.
