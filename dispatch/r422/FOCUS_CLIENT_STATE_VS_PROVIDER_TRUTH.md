# R422 — Focus: the gift can appear without an email confirmation

**Status:** SOURCE-ONLY / NO-SEND / NO-CMS-WRITE / NO NEW LIST. Owner: Dispatch/Focus consent QA, with Claude owning production analytics. Date: 2026-11-17 (03:34–03:40 PT). Source-of-truth: [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Revenue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Master six-issue [draft #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), independent gates #201, previous release proof #2858 remain unchanged.

## New source-of-truth observation (read-only)

The **published** [Focus page #1579](https://finalvestige.com/focus/) was read from authenticated WordPress on Nov 17, 2026. Its inline script looks for a `subscribe` URL parameter and reveals `#fvf-gift` whenever that parameter is nonempty and is **not** exactly one of `invalid_email`, `error`, `blocked_email`, `opted_out`, or `blocked`. It also reveals the gift when Jetpack's local form container acquires the CSS class `is-subscriber`. It does **not** call a backend to verify current email consent, nor does it emit a confirmed-signup event.

Because the same live page explicitly says **the PDF may be opened before email confirmation**, this is not by itself a security defect or an unauthorized product release. It is a **measurement boundary**: a browser state that makes a free download visible must never be reported as a provider-confirmed subscriber, an eligible email recipient, a received welcome email, or a paying customer.

| Observed or modeled client condition | Gift visible | Evidence of verified opt-in |
|---|---|---|
| No query / no subscriber class | No | No |
| `?subscribe=success` | Yes | No |
| `?subscribe=anything` | Yes | No |
| `?subscribe=blocked` or `?subscribe=invalid_email` | No | No |
| Local `is-subscriber` CSS class | Yes | No |
| Genuine backend confirmation with separately attested identity and permission | Not inferable from this script | Only an authenticated provider witness can establish it |

These client decisions were **modeled and tested** against the inspected script's conditions; they were not a live Chromium DOM or inbox acceptance run.

## November 17 recipient truth (11:36–11:37 UTC)

Authenticated Jetpack diagnostics: newsletter `subscriptions=true`, `site_can_send=true`, post automatic emails `email_new_posts_by_default=false`, email format `full`, reply-to `no-reply`, from name Final Vestige Studios. Platform newsletter counters total **3**, confirmed **3**, unconfirmed **2**, suppressed **0**. Separate Stats counters Reader/WordPress.com **3**, direct email **0**, comments **0**, partial **false**. These are **not additive** and cannot establish the number of unique, currently email-eligible inboxes. The most recent five post notification records show `never_sent_opted_out`, not proof that all historic sends failed.

Welcome copy still links to the **52-page** Seven Day Focus Fieldbook; the PDF is a configured media item (ID #1737, previously confirmed). A scoped connected Gmail search for the exact current welcome phrase and Fieldbook title (after Oct 28) returned **no matches**. One older WordPress confirmation exists; a confirmation request is not the actual Fieldbook welcome or a guarantee of inbox delivery. No personal addresses, confirmation tokens, or message contents are stored here.

## Production event contract (proposed, not implemented)

**Exactly one** `confirmed_signup` event per opaque provider record key, and only after Claude/Focus obtain an authenticated record showing: this existing Jetpack provider, newsletter-purpose consent, current confirmed state, eligibility after unsub/suppression, and a one-time deduplication key. Repeated form submissions, browser query strings, PDF clicks, success text, browser storage, and Reader follower totals are explicitly **excluded**. The standalone `consent_truth_gate.mjs` is a synthetic fail-closed acceptance prototype, not an integration or a data pipeline.

Expected evidence ladder:

1. **FOCUS_LANDING**: source-tagged qualified-human visit from Grok's real asset ID, as collected by Claude's existing analytics (no duplicate script)
2. **FORM_INTENT**: consent wording shown / client submission — **not** a lead
3. **PROVIDER_CONFIRMATION**: authenticated, deduplicated Jetpack record and permission — **eligible** for one `confirmed_signup` event
4. **WELCOME_RECEIPT**: privately authorized received inbox/MIME witness; configuration alone does not establish delivery
5. **GUIDE_CTA**: one appropriately sourced, founder-approved guide click, strictly separate from order
6. **PAID_CONVERSION**: independently reported paid/settled order, refund and fees, with appropriately consented attribution

Identity-safe grouping: `utm_source=<actual_platform>`, `utm_medium=organic_social`, `utm_campaign=<topic>_pilot_2026_11`, `utm_content=<Grok_real_asset_id>`. In an eventually authorized Dispatch email, use `utm_source=dispatch`, `utm_medium=email`, `utm_campaign=dispatch_pilot_2026_11`, `utm_content=issue_01` (and corresponding issue numbers) only if Claude verifies preservation of original acquisition attribution. Never put subscriber email or health/identity data in UTMs.

## Direct owner action and pass/fail

**Focus/Claude:** Read an authenticated, consented eligibility record *privately*, reconcile dashboard total/confirmed/unconfirmed with follower categories, document dedup and correct purpose scope, inspect any welcome delivery evidence without copying addresses to GitHub. **PASS** only for verified provider event; otherwise **HOLD**.

**Dispatch/Founder:** Witness an actual **non-sending WordPress native Preview** and verify a lawful postal footer and functional unsubscribe, without issuing a test email. Official guide: https://wordpress.com/support/newsletter/email-appearance/ (reviewed Nov 9, 2026). **PASS** only with captured actual template evidence, not offline mockups.

**Mind/Commerce:** named Final Vestige Inspire3 **EMAIL** authorization, approved creative/SKU, issued earning URL, live vetted warm-up guide, actual referred checkout/refunds and settlements. As of this run none established; keep Issues 03 and 05 `HOLD_MERCHANT`.

**Founder:** may approve use of reviewed copy and actual sends only in a separate explicit final campaign decision. None is granted by this prototype. Homepage flagship remains priority one; frozen homepage PR #49 untouched.

**Business measurement:** independent paid net revenue per 1,000 audited qualified-human sessions stays **NOT COMPUTABLE** until actual orders, refunds/fees, and human-session denominator are verifiable. No fabricated A/B conclusions with three dashboard subscribers.
