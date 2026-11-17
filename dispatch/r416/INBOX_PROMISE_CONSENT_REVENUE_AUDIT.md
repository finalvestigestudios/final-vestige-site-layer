# Dispatch R416 — acquisition promise versus actual email delivery: conversion-critical release audit

**Classification:** DRAFT / INTERNAL / HOLD_UNSENT. **Related:** [Dispatch master #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [canonical six drafts #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), [independent release QA #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), [revenue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Stacked on [Dispatch R415 #2827](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2827) at `7233c3d2f5d811b8d579b672032d62ae7fcc35c1`. Frozen homepage PR #49 not touched. All six canonical issues and six candidate alternatives remain unchanged.

## New P0 conversion finding: the site promises publication-tied emails while actual post-email delivery is deliberately OFF

Authenticated live WordPress **page 523** (/dispatch/) currently says, “New investigations and archive finds by email, when we publish them” and also “You'll also get new investigations and useful finds from the archive when we publish them.” The live Focus page **1579** likewise says The Dispatch is “sent when we publish them.” These are **prospective acquisition promises**, not evidence of consent or a delivered email. The published forms use the same native Jetpack subscribe infrastructure; Dispatch's form success message asks for a confirmation and tells the user the welcome contains the Fieldbook. The Focus page displays a downloadable PDF after certain URL-state signals: this display is not confirmation of email eligibility.

Meanwhile, authenticated Jetpack `get_settings` at **2026-11-17 05:31:59 UTC** reports `subscriptions=true`, `email_new_posts_by_default=false`, full-body email format, `reply_to=no-reply`, sender display “Final Vestige Studios,” and a configured 52-page welcome message containing the existing PDF URL. The `status` response at **2026-11-17 05:31:53 UTC** shows five recent published investigations whose post notifications were **never_sent_opted_out** because their per-post send flags were false. `site_can_send=true` describes technical capacity, not evidence that anyone was eligible, notified or delivered. It does **not** prove that every historic manual message was unsent, nor does it mean the founder should enable automatic emails. This divergence is a **subscriber-expectation and conversion-trust risk**, not an allegation of consent fraud or a demand to turn on mass mailing.

**Safe remedy, not executed:** Change the prospective wording only after founder and site-owner copy approval to “occasional, individually approved investigation and archive emails,” making clear that new site posts do **not necessarily** trigger newsletters. Align the same claim on /dispatch/, /focus/, any sitewide signup overlays, and the welcome copy. Test copy before any future publication. Never switch automatic emails on as a shortcut, never message current subscribers to rectify wording without the founder's specific contact approval. Suggested exact copy appears in `R416_CONSENT_COPY_FOR_REVIEW.md`.

## The actual subscription denominator remains UNRESOLVED

Live Jetpack subscriber dashboard: `total=3`, `confirmed=3`, `unconfirmed=2`, `suppressed=0`, `paid=0`. Independently queried `wpcom_jetpack_stats_followers`: **3 WordPress.com Reader followers, 0 direct-email followers**, `partial=false`, timestamp of this sprint. The categories do not necessarily identify distinct human inboxes and cannot be added into five subscribers or treated as three deliverable emails. In particular, three dashboard “confirmed” values and zero direct-email followers are an actionable taxonomy/eligibility conflict. The connected read-only interface does not expose recipient-level confirmation, permission scope, suppressions or deduplicated inbox eligibility. **Actual unique email-eligible recipients: UNKNOWN, not zero, three, or five.** No subscriber emails, hashes derived from inboxes, individual events or secrets appear in this PR.

The welcome is **CONFIGURED**, not witnessed arriving after double opt-in. A previous October 25 confirmation request is **not** a proof of completed confirmation or welcome delivery. Searches of the connected mailbox during this sprint found no matching “Welcome to The Dispatch” or vendor-specific acceptance evidence, but search absence is not a global negative proof. The free PDF's existence is not evidence that a subscriber received it.

**Owner:** Claude/Focus should compare, privately and read-only, authoritative Jetpack recipient identifiers and eligibility states, suppressions, double-opt-in timestamps and welcome-delivery records if the provider exposes them. Accept a single deduplicated `confirmed_signup` only after provider confirmation AND an email-eligible state. The existing front-end `subscribe` parameter, Focus gift visibility, a submit event, a dashboard aggregate and a WordPress Reader follower must **never** generate that event. Aggregate proof counts and opaque restricted receipt IDs may be shared; nothing identifying a subscriber should enter GitHub.

## Merchant approval, no purchase links, and zero presell release

Official seller research rechecked for **Zen12** and **Hypnosis Live Total Focus**:

* Zen12's official `https://zen12.com/about` describes 12 levels, four sound options, 12-minute sessions and asserts equivalence to an hour of meditation. The program features are merchant descriptions; the equivalence and advertised psychological benefits are **not independently substantiated for the SKU** merely by literature on mindfulness in general. No countdown price or result promise belongs in a subscriber-facing message without appropriate verification.
* Total Focus's official product page `https://hypnosislive.com/mental-skills/total-focus` describes a 33-minute, 47-MB MP3; public price presentations vary (single recording versus bundle). The `https://hypnosislive.com/faq` fourteen-day refund description also specifies a **maximum of five refunded sessions per year**. This is seller policy text, not verified referred-checkout terms. The vendor's claims about exceptional concentration or “reprogramming” are not independent product results.
* An Inspire3 public affiliate portal and any public “affiliates” link **do not** authenticate named Final Vestige affiliate acceptance or authorization to use email as a marketing channel. There is no authenticated issued earning URL for these exact SKUs, no verified eligible live first-party guide leading to a reviewed referred checkout, and no independently reported paid settlement.
* Mind & Affiliate Studio owns official creative-rights checking, partner permission, independent presell content and commercial landing pages. Dispatch owns **email copy, subject, disclosure placement and recipient release**. Do not adopt unapproved A/B claims or substitute a merchant homepage link because the buyer guide is blocked.

Commercial issue **03 Zen12** and **05 Total Focus** remain `HOLD_MERCHANT`; their primary commercial CTA is **inactive**. Same-issue, near-offer disclosure must accompany any later active recommendation. Maintain the canonical **four editorial : two commercial** slots; the alternatives in R415 remain `NOT_ADOPTED`.

## Why the current HTML/plaintext assets cannot be called production email-safe

Each candidate has an offline HTML/TXT specimen at a pinned GitHub blob. That proves an authoring artifact exists, NOT that Jetpack will use that HTML or render a separately configured preheader. WordPress's currently documented newsletter workflow uses the post title and full/excerpt post content; native **Preview email** is available in the editor, distinct from the “Send test email” action. The connected tools do not expose that authenticated graphical editor, and the founder has not authorized creating or updating draft posts. **No native preview or received email was performed.**

The configured `reply_to=no-reply` is not an unsubscribe. The Jetpack preview must visibly show a **valid physical mailing address belonging to Final Vestige** and clear opt-out; an Automattic address in a WordPress confirmation email or a merchant's UK address cannot be substituted. A preview shows appearance only; a functional unsubscribe and handling of suppression must be tested separately with specifically authorized, consented receipt and **not** against a real subscriber without approval. A commercial letter also needs sender truth, unambiguous commercial character and nondeceptive subject. The FTC's CAN-SPAM guide requires accurate header and subject, valid physical address, conspicuous opt-out, and honoring opt-outs within ten business days.

## Six-slot purchase-path mapping (all HOLD)

| Slot | First-party destination / proposed action | Commercial gate | Evidence needed |
|---|---|---|---|
| 01 Editorial — change blindness | Published Nov 2 investigation; “Investigate the change-blindness experiments” | None, but release HOLD | Founder adopts alternative; native email + consent/footer |
| 02 Editorial — Franklin commission | Published Nov 2 Mesmerism investigation | None, but release HOLD | Founder adopts alternative; source citations + native preview |
| 03 Commercial — Zen12 | NO live buyer-guide CTA authorized | `HOLD_MERCHANT` | Named SKU email rights, eligible landing guide, issued link, actual terms |
| 04 Editorial — Apollo 1 | Published Aug 20 investigation | `HOLD_COPY` | Founder accepts chronology correction and dated site-standard procedure if needed |
| 05 Commercial — Total Focus | NO live buyer-guide CTA authorized | `HOLD_MERCHANT` | Specific product rights, refund restrictions at referred checkout, published guide |
| 06 Editorial — evidence log | Published “The Page That Changed” guide | None, but release HOLD | Verify welcome actually arrived so CTA progresses, not repeats signup |

The four editorial destination links were independently corroborated by the site content connection: published WordPress post **1922** (change blindness), **1924** (Mesmerism), **434** (Apollo 1), and published page **2209** (“The Page That Changed”). A public web 429 or fetch failure alone is not a dead-link verdict; the authenticated WordPress records establish the current published canonical URLs, not a functional inbox click. **This makes the 4 editorial CTA destinations plausible, not the 2 commercial ones.**

## Experiment contract with no new platform, scripts or fake conversions

**Hypothesis:** Better expectation alignment and verified welcome delivery improve the chance that an *eligible* subscriber reads an evidence-backed Dispatch and later voluntarily visits ONE approved buyer guide. This is not statistically tested and is not a license for behavioral automation.

**Attribution convention for future reviewed creative only:** Grok's approved source path uses `utm_source={actual platform}`, `utm_medium=organic_social`, `utm_campaign={topic_cluster}_pilot_2026_11`, `utm_content={immutable asset_id}`; it lands at the existing /focus/ or relevant source article after Claude QA. If the founder later approves a Dispatch send, the newsletter-owned link may use `utm_source=dispatch`, `utm_medium=email`, `utm_campaign=dispatch_mind_pilot_2026_11`, `utm_content=issue_01..06`, subject to Claude's existing privacy/measurement setup; do **not** put untested tracking parameters into links now. Carry the original social asset only when a permitted, privacy-preserving first-party attribution mechanism actually exists; do not place a person-level identifier in a URL. Don't double-count newsletter clicks as signups, customers or sales.

**Server/provider truth required:** (1) qualified-human session with legitimate asset attribution, (2) relevant first-party CTA click where correctly instrumented, (3) provider-authoritative deduplicated confirmed-and-eligible signup when applicable, (4) merchant or first-party independently settled paid order, (5) returns/refunds and fees. `realized_net_revenue_per_1000 = 1000 * (settled_gross - refunds - fees) / qualified_human_sessions` only with nonzero audited denominator and authenticated settlement records. If either is missing, `NOT_COMPUTABLE`, **not zero**, and no guessed A/B uplift from a 0–3-recipient population. Group only aggregated 7-/30-day cohorts, clearly marked tiny sample.

## P0/P1 conversion-first owner docket

| Offer → funnel step | Blocker | Change / controlled test | PASS/FAIL evidence now | Owner |
|---|---|---|---|---|
| The Dispatch expectation → qualified signup | “When we publish” promise conflicts with default-off and five never-sent post notices | Founder approves amended occasional-send consent copy; Claude applies later only under release authorization | **P0 FAIL alignment / no live changes** | Founder + Claude/Focus + Dispatch copy |
| Focus → confirmed eligible reader | Dashboard3/3/2 versus Reader3/email0; unknown eligible IDs | Restricted provider truth reconciliation + welcome/PDF receipt witness | **P0 UNKNOWN**, not lead count | Focus / Claude |
| Zen12 guide → purchased SKU | Named EMAIL permissions, authorized earning link, guide and actual checkout absent | Mind authenticates source-of-truth private agreement and seller terms | **P0 HOLD_MERCHANT** | Mind / Commerce |
| Total Focus guide → purchased SKU | Same permission and checkout/refund limitations | SKU-specific private email-rights/checkout proof | **P0 HOLD_MERCHANT** | Mind / Commerce |
| Approved Dispatch → compliant delivered email | Native editor, FV address and working unsubscribe not witnessed | Founder-authorized preview only (NOT a test send); separate later opt-out authorization | **P0 HOLD_UNSENT** | Dispatch / Founder |
| Grok asset → paid revenue | No audited qualified sessions/settled transaction joins | Claude reuses existing events, logs opaque proof and aggregates cohorts | **P0 NOT_COMPUTABLE** | Grok / Praxxis / Claude |
| Apollo 1 editorial source → trust | Current canonical Issue04 uses ambiguous fourteen-second title | Founder considers R412 precise correction, with correction rules | **P1 HOLD_COPY** | Dispatch / Founder |

**Release:** zero sends, zero test emails, zero changes to WordPress, subscriber lists, signup settings, Grok production, merchant links, paid services or frozen homepage PR #49. No merge. Existing source-controlled candidates remain unadopted. Every issue remains `HOLD_UNSENT`. This audit is decision evidence, not a legal opinion or proof of merchant approval.

**Primary references:**
- Live: https://finalvestige.com/dispatch/ ; https://finalvestige.com/focus/ ; https://finalvestige.com/editorial-standards/
- Platform: https://wordpress.com/support/newsletter/email-appearance/
- Merchant: https://zen12.com/about ; https://hypnosislive.com/mental-skills/total-focus ; https://hypnosislive.com/faq
- Rules: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Attribution coordination: https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit
