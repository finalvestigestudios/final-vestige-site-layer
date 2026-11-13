# R322 | One Jetpack newsletter, two legitimate signup paths

**Status:** DRAFT REVIEW / NOT A RELEASE / ALL SIX ISSUES HOLD_UNSENT; commercial 03 and 05 HOLD_MERCHANT. **No send, test email, WordPress draft/post/write, subscriber change, affiliate link, tracking deployment or expense.** This is a targeted corrective sprint, not a new newsletter platform or list.

## Material correction to R319 #2286

The previous event classifier required an **unconfirmed → active** history before it would count a new confirmed signup. That guards against counting old followers as new leads, but it has a material **false-negative** for existing WordPress.com account holders. WordPress says people without WordPress.com accounts receive confirmation mail first, whereas an existing WordPress.com account can subscribe and receive the welcome immediately, skipping the email-confirmation step. Source: [WordPress newsletter settings (last reviewed 26 October 2026)](https://wordpress.com/support/newsletter-settings/).

**Correct rule:** count a newly activated, explicitly opted-in, email-eligible *site* subscription **only from authenticated, timestamped provider enrollment evidence**, with two permitted proof routes:

1. **New email subscriber:** confirmed email-link completion tied to this site's subscription; do not count merely submitting the form.
2. **Existing WordPress.com account:** provider-verified new *site subscription* activation, with verified account route; **no claim that a separate confirmation email was received**.

Both require consent to The Dispatch, active email delivery eligibility, unique opaque subject/event references, deduplication, and the first actual site enrollment timestamp for 7/30-day cohort assignment. Neither a first-seen active snapshot, Reader follow, PDF access, browser `?subscribe=` value, republished historical record nor a previously subscribed WordPress.com account is a new event.

R322's pure JS classifier and 27 native Node tests exercise both paths, source-origin and privacy failure cases. **The string `authenticated_jetpack_site_event` is merely a mock adapter contract. This program cannot authenticate the provider.** Claude/Focus must validate provider events *outside* GitHub, retain private witness records privately and export only aggregated counts. If Jetpack does not expose sufficient event evidence, report `confirmed_signup=UNKNOWN` for actual operations; do not fabricate a zero or call a Reader follow a subscriber.

## Authenticated site snapshot — 13 November 2026 05:34 UTC

- Jetpack Newsletter ON; `site_can_send=true` is a *capability*, **not** sender approval.
- Default new-post emails OFF; full-text format; `from_name=Final Vestige Studios`; `reply_to=no-reply`. Do not change.
- Latest total/confirmed/unconfirmed **3/3/2**, overlapping categorization; neither sum nor assume 3 email-eligible recipients.
- Last five post events are `never_sent_opted_out`, explicitly `send_subscription=false`, **not a lifetime zero-sends certificate**.
- Welcome text contains the 52-page Focus Fieldbook PDF link and promises archive finds; **actual receipt, final PDF delivery and transport headers remain unverified**.
- /dispatch/ page #523 and /focus/ #1579 published; earlier R320 reproducibly exposed browser query-dependent Focus gift UI. A visible gift is not new consent.
- Live Editorial Standards require primary sources, uncertainty and independent commercial judgments.
- Public /dispatch/ rendering of a Jetpack form cannot be concluded broken from the editor's fallback anchor alone.

## Source-of-truth commercial and legal checks — all HOLD

**One intended offer:** Zen12 **Premium** (twelve levels / 48 MP3). Beginner and Advanced are six levels / 24 MP3 each; never imply all three are the full program. The seller asserts a 12-minute session can replace an hour of meditation: **not independently established**. Product sales page: https://zen12.com/ . Follow-up Issue 05 still reserves Hypnosis Live **Total Focus** (merchant page https://hypnosislive.com/mental-skills/total-focus describes 33 minutes / 47 MB). Seller page on 13 November 2026 displayed $24.44 and a seller-described 14-day refund; previous captures differed, proving price/terms are *volatile*. Do not quote price, refund or conversion promise in sending copy without authentic checkout/review evidence.

Public https://affiliates.inspire3.com/ invites applications and describes issued promotional links; it **does not** evidence Final Vestige account acceptance, allowed email marketing, partner creative license, actual publisher link, payout, SKU or 2026 checkout terms. Mind #171 owns partner evidence and publication of vetted warm-up guides. Current Mind draft PR #2298 and earlier guides are *NOT LIVE*. No newsletter CTA should turn a proposed guide into a live offer or bypass the guide to a merchant.

Commercial primary purpose is assessed per **final email**, even for predominantly editorial editions. Need Final Vestige's own valid mailing address (not Automattic's, nor Inspire3's London address), native received-email footer and functional unsubscribe, sender and honest subject/preheader, immediately adjacent commission disclosure, and explicit final approval. FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . WordPress: https://wordpress.com/support/newsletter/email-appearance/ and https://wordpress.com/support/newsletter/send-newsletter-emails/ . Native preview can be viewed without activating a send toggle but needs a draft/editor workflow separately approved; no such real WordPress preview or test email occurred.

## Campaign preservation and non-sending recipient progression

| Issue | Type | Editorial destination | Release decision |
|---|---|---|---|
| 01 mind / attention | Editorial | Existing FV investigation (original Puységur destination duplicates 02; R314 alternate NOT_ADOPTED) | HOLD |
| 02 historic witness | Editorial | Published Puységur document page; R321 alternative NOT_ADOPTED | HOLD |
| 03 12-minute practice | Commercial draft | **Unpublished Zen12 Premium independent warm-up guide** + future verified earning link | HOLD_MERCHANT |
| 04 Apollo 1 evidence | Editorial | Published Apollo evidence; 14-seconds subject revision pending | HOLD |
| 05 evaluate hypnosis audio | Commercial draft | **Unpublished Total Focus independent warm-up guide** + future verified earning link | HOLD_MERCHANT |
| 06 evidence log | Editorial | Existing /focus/ welcome Fieldbook; avoid asking established subscribers to opt in again | HOLD |

**Conceptual path, not automated or scheduled:** Grok's genuine published asset ID → topical independent page → visitor elects existing Jetpack Subscribe → *either* verified email-link confirmation *or* verified WP-account immediate site activation → configured welcome/Fieldbook (delivery requires independent witness) → relevant source-led issue → qualified topic-based guide after Mind authorization → settlement reported by merchant. Existing subscribers should never be placed in a second list or coerced into resubscribing. Jetpack is post-triggered; the source plan is **not** proof that time-based drip segmentation can be executed with this stack. No send calendar approved.

## Measurable business acceptance

`confirmed_signup` = uniquely new site enrollment verified by the provider through either route. `attributed_confirmed_signup` requires additionally a legitimate first-party Grok join; a UTM by itself is not a join. `paid_conversion` requires authenticated fulfilled/settled order or merchant-issued paid commission; click, PDF access, checkout intent and email open are **not** money. 7-day and 30-day cohorts use provider event time, not observation time. KPI: `1000 × (settled gross - actual refunds - fees) / qualified-human sessions`, only if the actual numerator and denominator are both verified. Otherwise **NOT COMPUTABLE**; with three total followers no credible A/B performance claims.

## Engineering handoffs and conflict safety

- **Claude/Focus #129:** identify whether provider API exposes new-site enrollment events for existing WordPress accounts and email-confirmed users; prove email vs Reader eligibility privately; deduplicate and verify Welcome receipt without list export or test message. If unavailable, mark event count UNKNOWN, not a fabricated metric.
- **Mind/Commerce #171:** Final Vestige-specific permitted EMAIL use, issued earning link, Premium tier, approved/actual LIVE warm-up guide, merchant claim and refund/checkout terms, published-disclosure placement. No direct merchant CTA.
- **Dispatch/Founder #174:** review 4:2 creative decision log, verify real native Jetpack recipient preview and legally complete post-send footer with *separate* authorization, and final audience/schedule approval. No email sent.
- **Grok/Praxxis TASK-008 / Claude #820:** real source asset IDs and `utm_medium=organic_social`; preserve Grok content ownership and existing tracking stack.
- **Commerce #820:** independent settled order and fee/refund reporting; aggregate cohort revenue only.

Original master PR #175 at exact `d57ccdba3aee8f065e143e101c2945f4f3d01647`, independently read 8/8 remote blobs and ran its six native Python tests 6/6 PASS. PR #201 original QA artifacts and R319 #2286 untouched. R322 branch is based directly on master #175 to avoid conflicting stacked editorial drafts. No changes to frozen homepage PR #49.

**Evidence labels:** BUILT = new read-only source/testing package; TESTED = 27 native Node tests and 6 master Python tests on byte-identical GitHub source; NOT LIVE = provider authentication, welcome delivery, actual inbox/legal footer, published offer, partner rights, consented human attribution and paid revenue.
