# Dispatch R308 — the six-issue *broadcast* is not a signup-relative sequence

**2026-11-12, 07:30 PT. REVIEW-ONLY, UNSENT, NO CMS CHANGES.** Owner: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Companion offer authority: [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Commercial evidence owner: [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Original immutable six-issue master: [draft PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), `d57ccdba3aee8f065e143e101c2945f4f3d01647`. Keep founder homepage priority and frozen PR #49 untouched.

## Material operational finding (distinct from R306 post-send release gate)

The six weekly issues are *calendar broadcasts triggered by individual WordPress post publication* under the current Jetpack newsletter. They are **not** a subscriber-specific six-week onboarding drip. A subscriber confirmed after Issue 03 has published cannot be assumed to receive Issues 01–03 by email. A welcome email containing the Fieldbook may be configured, but is **not** proof of individual receipt of a six-issue sequence.

- WordPress official instructions: https://wordpress.com/support/newsletter/send-newsletter-emails/ (reviewed 2026-11-09) — publishing a post is the newsletter email action, the post title becomes email subject, the per-post email toggle can override the default, and a *non-sending* Preview email exists in the editor.
- WordPress official subscriber statuses: https://wordpress.com/support/subscribers/ (reviewed 2026-11-04). Reader followers, unconfirmed subscriptions, paused/bounced recipients and a subscribed email recipient are not the same population.
- WordPress newsletter category option: https://wordpress.com/support/newsletter-settings/enable-newsletter-categories/ (reviewed 2026-10-06). Categories are available but **currently disabled**; do not treat this as audience-interest segmentation or change the setting without founder approval.
- WordPress newsletter defaults: https://wordpress.com/support/newsletter-settings/ — turning new-post automatic sending OFF does not forbid a single post's send toggle from being enabled.

**Correct terminology in every proposal:** “six weekly editorial releases to whoever is email-eligible at the time,” never “every new subscriber receives six timed emails.” This does not require another platform. If the founder wants genuine relative-to-signup automation or behavior-triggered commercial segmentation later, that needs a separate functionality/consent assessment, not claims that the present setup already does it.

## Current read-only state (2026-11-12T15:30:52 UTC)

Authenticated WordPress Jetpack: newsletter enabled, site can send, `email_new_posts_by_default=false`, content `full`, sender Final Vestige Studios, reply-to no-reply, welcome contains the 52-page Seven Day Focus Fieldbook URL. The diagnostics show `total=3, confirmed=3, unconfirmed=2, suppressed=0`. WordPress's total excludes unconfirmed records; the categories are not additive. `newsletter_categories_enabled=false`. Five recent listed posts were `never_sent_opted_out`; this is NOT proof of a lifetime no-send record.

**Still unknown:** how many of those three are email-eligible per subscriber's **Email subscription** status; exact individual welcome delivery; received Jetpack unsubscribe/footer and valid Final Vestige postal address; full native email preview; any approved Final Vestige Inspire3 affiliate account/EMAIL channel terms, earning URL, approved live guide or settled attributable order.

Read-only connected Gmail query on 2026-11-12 found a 2026-10-25 **Confirm your subscription** message, but no matching final “Welcome to The Dispatch” / “Seven Day Focus Fieldbook” email in that connected mailbox for the scoped October–November window. This negative search **does not prove no welcome was delivered to another mailbox**. Affiliate-related inbound promotional messages are NOT Final Vestige-specific affiliate or email-promotion authorization. No subscriber list was read, exported or contacted.

## Synthetic cohort demonstration — not a campaign schedule

Source: `broadcast_cohort_gate.py` plus 27 native unit tests. Example start `2027-01-01T12:00:00Z` is **invented test fixture, never a proposed send date**.

| Fictional cohort | Email confirmations | Issue 01–03 | Issue 04–06 |
|---|---|---|---|
| Reader A | Before first hypothetical publication | Editorial eligibility still held; Issue 03 merchant hard hold | Editorial held; Issue 05 merchant hard hold |
| Reader B | 21 days after first publication (exact fourth issue instant) | All three earlier issues are `joined_after_publication` | Editorial held and commercial still hard held |
| Reader C | Only Reader follower, or pending email | Not email-eligible | Not email-eligible |

A synthetic `theoretically_eligible_not_sent` state, even if all mocked attestations are true, **never sends or predicts receipt**. Actual subscriber frequency preferences, deliverability and server operations are not simulated. A single confirmed count does not imply permission to send commercial content; the optional `consent_for_commercial` test flag is an intentionally stricter FV editorial safeguard, **not a claim that CAN-SPAM requires opt-in**.

## Conversion-first one-offer decision

**ONE high-intent audience hypothesis:** readers who liked the documented perception experiments and want a short, practical concentration routine but are skeptical about grand audio promises. **ONE candidate offer:** Zen12, presently **NOT approved** for FV email promotion. No alternate Hypnosis Live placement should be activated to evade this gate. Maintain the founder's original **4 editorial : 2 commercial-review-reserved** mix (Issues 03/05). An optional offer mention has no revenue meaning before a real permitted purchase.

**Intended steps, after legal and founder approval:**

1. Published, genuinely source-aligned Grok asset `asset_id` → permitted UTM-tagged URL to Focus/archive. Attribution owner: Grok/Praxxis/Claude.
2. On-site relevant evidence article → Focus Fieldbook offered freely, separate from signing up. Treat the `?subscribe=` gift-panel state as a UI indicator, not provider-confirmed `confirmed_signup` (see [R307](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2209)). Owner: Claude/Focus.
3. Actual provider-confirmed subscriber, deduplicated by a private stable provider ID and confirmation transition, not by browser query string, request count or WordPress.com Reader follower. Never store subscriber emails in public GitHub. Owner: Claude/Focus.
4. The Dispatch's weekly published editorials, **only to email-eligible recipients when each respective post is published**, not historical backfill or behavioral drip. Owner: Dispatch/Founder.
5. Commercial edition 03 only after merchant account-specific EMAIL permission, an exact approved earning link, live independent FV warm-up guide, copy/claims/refund/price checked against the exact official seller sales page, and adjacent affiliate disclosure. Owner: Mind/Commerce; release Founder.
6. Independent reported *settled paid order or commission* and refunds/fees → realized net revenue, not a visitor or link click. Per-asset 7/30-day cohorts should be labeled unknown absent reliable attribution. Owner: Commerce/Claude.

**Attribution convention proposal, not deployed:** `utm_source=youtube|tiktok|instagram|...`, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=<verified_published_asset_id>`. For email → guide after approval, use `utm_source=dispatch`, `utm_medium=email`, `utm_campaign=dispatch_mind_pilot_2026_11`, `utm_content=issue03_zen12` (no person identifiers). Preserve consent, source and privacy. Confirm with Claude before any URL is activated. Do not emit a new GA4/pixel or duplicate confirmed_signup event.

## Direct-response and editorial diagnosis

The existing Issue 03 guide CTA is the literal inactive `[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]`; Issue 05's is the corresponding inactive Hypnosis Live guide token. These cannot be described as live conversion paths. Both contain a useful *secondary* live archive/Focus link; those links remain editorial alternatives, not evidence of merchant readiness or an approved purchase CTA. The commercial editions should not imply the first-party evaluation guides are published. Original Issues 01/02 link to the same Puységur archive; R300/R301 alternatives are available but not adopted. Issue 04's fourteen-second subject needs factual correction (R302). Issue 06 asks existing subscribers to visit a signup page (R299). **Do not rewrite #175 without reviewing the latest founder decisions.**

Seller-specific source alignment: https://zen12.com/about advertises 12 levels and four formats, but “meditates for you” and effortless brainwave benefits are *seller promises*, not independently validated product outcomes. https://hypnosislive.com/mental-skills/total-focus describes a seller-advertised 33-minute / 47 MB audio; visible prices have differed across indexed/live snapshots, so **do not include a fixed price or refund promise** until time-of-release checkout and agreement verification. Public Inspire3 material does not prove FV acceptance, email rights or commission attribution.

FTC CAN-SPAM commercial messages require truthful subjects and sender information, valid publisher postal address and effective opt-out. A valid registered PO Box or compliant private mailbox can qualify; an Automattic/WordPress address is **not automatically** FV's address. https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . Affiliate disclosure should be intelligible alongside the actual offer and not buried in legal boilerplate.

## Verified tests, release gate and owners

- Original PR #175 checked against *eight exact Git blob SHAs*, locally restored from the earlier R304 native-master package: **6/6 original Python unit tests passed on this run** (same exact current PR head).
- New R308 pure Python cohort module: **27/27 native unit tests passed**, including late confirmation, absent/paused/bounced Reader-only statuses, opt-out order, commercial permission, unpublished guide, final approval, missing postal/unsubscribe, duplicate synthetic ids, date safety and no-PII guard.
- Local tests do not establish real platform eligibility, email rendering, consent, authorization or delivery. GitHub CI/native WordPress email preview NOT run. No audience data used.
- No scheduling or post publication, emails including test messages, settings changes, subscriber exports, social edits, affiliate activation, purchases, paid services or live site changes permitted.
- **Release: 6/6 HOLD_UNSENT; issues 03/05 additionally HOLD_MERCHANT.** Paid conversion and net revenue per 1,000 qualified human sessions: **not computable**.

### Priority offer → step → blocker → change → evidence → owner

| Offer → step | Blocker | Next action / experiment | Evidence | Owner |
|---|---|---|---|---|
| Zen12 → buyer guide → order | Email rights + live guide + earning link unknown | Request authenticated account/channel terms; non-sending merchant review | HOLD_MERCHANT | Mind / Commerce |
| Focus → confirmed subscriber | Current count ≠ email eligibility; gift panel ≠ consent | Private email-subscription status totals and actual confirmation event proof; no PII export | UNKNOWN | Claude / Focus |
| Dispatch → six-edition nurture | Publication-based broadcast ≠ per-signup sequence | Present honest timeline; no behavioral drip promise | 27/27 offline tests | Dispatch |
| Email → actual inbox | No authentic sender postal/opt-out or received Jetpack preview | Founder-approved read-only UI preview first; no test send | HOLD_UNSENT | Dispatch / Founder |
| Grok → qualified sessions | Actual immutable asset IDs unresolved | Source-tag audit with Praxxis, not new tracking scripts | UNKNOWN | Grok / Praxxis / Claude |
| Sales → net revenue | No settled order/commission/refund evidence | Read-only commerce reconciliation by owner | UNKNOWN | Commerce / Claude |

**Founder authority remains mandatory** for the final campaign creative, exact audience, any post/email sends, CMS changes or spend. This PR is an additive, unmerged reviewer-only evidence branch. Neither primary homepage work nor PR #49 was touched.
