# Dispatch R171 — cross-route subscriber truth and conversion readiness
**DRAFT ONLY / HOLD_UNSENT / 2026-11-06 22:34 UTC**

Owner [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), companion [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), strategy [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Stacked atop PR #1308 at `23b628498577eeb18f5dab9fb45fe72700578377`. Original pilot PR #175 and guard PR #201 unchanged; homepage PR #49 frozen.

## New read-only discrepancy to triage, not proof the guest form is broken
WordPress page **523 /dispatch/** stores a native `<!-- wp:jetpack/subscriptions ... /-->` block (authenticated edit-context). **The same page's view-context API output rendered "Subscribe" as an anchor back to `/?post_type=page&p=523` with no email entry field in that fragment.** The edit/render distinction is verified; **real signed-out public behavior is NOT VERIFIED**. Jetpack's dynamic block could differ by context or user. Do not infer that every visitor sees a broken self-link.

**Claude + Site QA acceptance**: without submitting real email addresses, inspect /dispatch/ signed-out at 320, 390, 768 and 1440px, then in WordPress.com logged-in state. Observe visible email input or expected platform-native subscriber handling, tab focus, button, redirect/loop, accessibility, console/network warnings, and user-state differences. Record only non-PII screenshots and outcomes. Keep native Jetpack block; do not substitute a new form provider or send an unauthorized test email.

## Previously reproduced Focus false-success exposure still live
Authenticated edit source page **1579 /focus/** includes `fvf-gift-v2`: arbitrary non-error `?subscribe=` query values and `is-subscriber` CSS-class checks can unhide the Fieldbook panel. **Visible success is not evidence of confirmed opt-in.** Proposed patch in draft PR #1272 remains unimplemented in production. `confirmed_signup` must never fire from that client-side logic or a PDF click.

## Current source-of-truth status (UTC 22:34)
- Jetpack newsletter enabled and sendable; automatic new-post emails disabled; full-content mode; From: Final Vestige Studios; reply: no-reply. Welcome configured with **52-page Focus Fieldbook** download link; actual received welcome **NOT VERIFIED**.
- WordPress counts total **3**, confirmed **3**, unconfirmed **2**, suppressed **0**. Counted and pending are **not additive**; follower report shows three WP.com followers and zero legacy email-only followers. **Email-delivery eligible recipients remain UNKNOWN** until provider-native subscription state is confirmed.
- The last five listed site posts reported `never_sent_opted_out`; do not generalize this to zero messages ever sent.
- Neither a native non-sending Jetpack *email preview*, delivered MIME, working unsubscribe, nor publisher physical postal address has been verified.
- Official products: Hypnosis Live seller advertises **Total Focus 33 minutes / 47 MB**; marketing efficacy, discounts, checkout and refunds are seller representations, not independent proof or authorized earning links. Zen12 seller describes 12 levels/48 recordings but named FV affiliate approval, email permission, actual earning links, and live approved guides remain unknown. **Commercial Issues 03 and 05 additionally HOLD_MERCHANT.**

## Conversion-first, one offer at a time
**Hypothesis only:** Grok's evidence-led perception topics will convert better to genuinely consenting Fieldbook readers, then relevant sourced guide readers, than to immediate seller pitches. Campaign remains **four editorial + two reserved commercial**; no alternative replaces the founders' original six drafts.

Define a single provider-authorized `confirmed_signup` event only on a verified status transition to opted-in EMAIL subscription, once per subscriber via privacy-preserving deduplication. A pageview, CSS class, confirmation invitation, PDF download, WordPress.com follow without email preference, or welcome *configuration* does not qualify. Never place raw email addresses, signed tokens or personal identifiers in analytics.

Once Grok and Claude approve measurement, use: `utm_source=<observed platform>`, `utm_medium=organic_social`, `utm_campaign=<topic_cluster>_pilot_2026_11`, `utm_content=<unique Grok asset_id>`. After approval, use distinct issue landing UTM IDs `dispatch_pilot_01` through `dispatch_pilot_06`. Do not activate tracked links or add duplicate instrumentation now. One relevant first-party editorial CTA per message; product guides only after Mind #171 explicitly verifies them.

**Primary KPI** = independently settled net revenue (gross paid orders minus settled refunds and fees, including losses) divided by qualified, deduplicated human sessions for exact 7/30 day cohorts, ×1000. No paid-order or session reconciliation provided: **NOT_COMPUTABLE**. A click, opt-in, partner button or page load is not a sale. Tiny sample means no A/B significance.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PROOF → OWNER
1. Fieldbook → confirmed subscriber → unsafe Focus visual-success script → validate PR #1272 and guest/provider status → **SOURCE FAIL, real receipt NOT VERIFIED** → Claude/Site QA + Dispatch.
2. Dispatch → newsletter sign-up → native block vs API self-link discrepancy → signed-out + WordPress.com browser comparison → **BROWSER REQUIRED** → Claude/Site QA.
3. Confirmed subscriber → Fieldbook welcome → configured, not verified delivered → non-sending provider record or authorized existing email evidence → **UNKNOWN** → Dispatch.
4. Zen12 → approved warm-up guide → missing email-promotion approval, earning URL, live guide → validate named affiliate terms and exact merchant page with Mind #171 → **HOLD_MERCHANT** → Mind/Founder.
5. Commercial newsletter → recipient → postal/unsubscribe and actual Jetpack rendering not verified → qualified footer + native non-sending preview, authorized evidence → **UNKNOWN** → Founder/Dispatch.
6. Buyer → independently settled paid conversion → missing paid orders, fees, refunds and attribution → reconcile real 7/30 day cohorts → **NOT_COMPUTABLE** → Commerce/Praxxis/Claude.

## Original research-aligned optional edition
New **UNSENT, unapproved Issue 01 alternative** `01-the-syllable-not-on-the-soundtrack.txt` tells the 1976 McGurk-MacDonald audiovisual speech experiment with its original audio-only controls, explicitly rejects overgeneralization, teaches a sensory evidence log, and routes to the already-live different (not identical) [Change Blindness investigation](https://finalvestige.com/2026/11/02/change-blindness/). Sources: [Nature original, 1976](https://doi.org/10.1038/264746a0); [MacDonald retrospective, 2017](https://doi.org/10.1163/22134808-00002548). Free editorial copy; no merchant or affiliate URL; footer placeholders MUST block send. HTML file is an offline reviewer, **not Jetpack email rendering**.

## Compliance / release governance
Use [FTC CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) for accurate sender/subject, clear commercial promotion, valid sender postal address, conspicuous functional opt-out and honoring requests; adjacent affiliate disclosure required for qualifying offers. Founder's separate final sign-off required for creative, recipient audience, schedule and any send. No sending, no website writes, list changes, merchant activation, checkout changes, new tools, costs, social posting or homepage PR #49 alterations.

**Local verifiable QA package** (outside repository; source-controlled code must be re-run independently after any future merge): 20 native Python tests for the read-only fail-closed provider truth gate PASS; twelve local plaintext/HTML checks PASS. All-release-attestation booleans remain false. Actual guest browser and received email NOT VERIFIED. This PR is for review only.