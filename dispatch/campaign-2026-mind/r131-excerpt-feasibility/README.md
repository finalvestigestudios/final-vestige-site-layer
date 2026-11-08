# R131: Excerpt-mode risk discovered — all six canonical email CTAs outside the visible opening
This is a separate DRAFT evidence package under Dispatch #174; original #175, guard #201, parent #1044 and frozen homepage #49 are not modified. Mind owner #171 retains all offer guides; Focus #129 owns consent integration; #820 owns commercial attribution. No WP writes, no email, no new tools, no subscribers accessed.

## What is actually observed
At 2026-11-05 06:30 UTC, authenticated WordPress Newsletter setting: `email_content_format=excerpt`, `email_new_posts_by_default=false`, welcome has public Fieldbook PDF link, `reply_to=no-reply`. Aggregate subscribers total 3, confirmed 3, unconfirmed 2, non-additive, actual email eligibility UNKNOWN. WordPress docs describe default excerpt as 55 words, while current Jetpack docs describe 350 characters; these are competing product paths, **not** a real email render. Exact original master PR #175 six Markdown files were independently read at SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`. All six canonical CTA destinations/labels are beyond both approximations. Both Issue 03/05 commercial disclosures are also beyond both. This means **ordinary excerpt delivery could omit the letter's value, intended action, and disclosures**; it is a high-impact, actionable CONVERSION risk, not proof of delivered mail.

## Implementation decision, no changes approved
Option A: Preserve excerpt mode; create exact founder-reviewed custom post excerpts with an honest short opening, one clear first-party CTA and required disclosure visible in a *native Jetpack preview*. It is a teaser, not a complete six-issue letter: founder approves tradeoff. Do not use inactive guide URLs.

Option B: Evaluate a full-text newsletter setting for complete story letters, but **DO NOT SWITCH SITEWIDE SETTINGS** without separate final founder approval; other manually emailed posts may be affected. Preview any More block behavior.

Neither option can be greenlit until an authorized WordPress editor Preview email and a **founder-authorized received test email** verifies CTA, preheader behavior, FV's own valid physical postal address and operational unsubscribe. WordPress default post title is typically subject; do not assume independently adjustable preheader. Keep automatic email on new post OFF.

## Reproduction / tests
- `node dispatch/campaign-2026-mind/r131-excerpt-feasibility/excerpt_guard.cjs` exits 2 on discovered risk, with JSON; reads only canonical files, no HTTP or write calls.
- `node dispatch/campaign-2026-mind/r131-excerpt-feasibility/test_guard.cjs` contains 12 synthetic QA guards.
- `canonical_excerpt_evidence.json` stores source blob hashes and each issue's two-model result. V8 executed synthetic 12 and source 6 exact-source checks. Native Node and hosted CI are **NOT YET VERIFIED** for the committed JS. An independent offline Python risk assessor also ran 8/8 native local synthetic tests, but it is separate from this PR and has not been claimed to run on the source checkout.

## Offer → step → blocker → change → evidence → owner
**Zen12 provisional → subscriber-to-guide:** guide PR #1047 is DRAFT/NOT LIVE and merchant named affiliate/email permission, tracking URLs, price/refunds and acceptable privacy are UNVERIFIED; fix with Mind-signed live first-party guide + permitted earning link + written acceptance; owner Mind #171; **HOLD_MERCHANT**.
**Fieldbook → real subscriber:** mere PDF reveal, dashboard count or an imported follower does not prove opt-in; require private native Email subscription status, first confirmed event, dedup opaque ID and welcome receipt; owner Dispatch #174 / Claude #129; **NOT VERIFIED**.
**Dispatch → full editorial value/CTA:** 6/6 CTAs missing both modeled excerpts and 2/2 commercial disclosure missing; choose authorized native post format/custom excerpt path, then real preview; owner Dispatch + Claude; **MODELED RISK VERIFIED, REAL RENDER NOT TESTED**.
**Grok traffic → paid order:** tag qualified assets as `utm_source=<social>&utm_medium=organic_social&utm_campaign=cluster_pilot_yyyy_mm&utm_content=<asset_id>`, email click `utm_source=dispatch&utm_medium=email&utm_campaign=mind_pilot_2026_11&utm_content=dispatch_issue_0N`; merchant settlement / fees / refund / qualified humans missing; owner Praxxis #820 and Claude; **NET/1000 NOT COMPUTABLE**.

## Legal/editorial holds
Six original editions HOLD_UNSENT. Issues 03 and 05 additional HOLD_MERCHANT. Adjacent commercial disclosures are required, not just an affiliate footer. No unsupported product efficacy claims. Do not import seller subscribers, claim sales from clicks or send any campaign email without founder's explicit final approval. No fake postal address.
Sources: https://wordpress.com/support/newsletter-settings/ ; https://wordpress.com/support/newsletter/email-appearance/ ; https://jetpack.com/support/newsletter/customize-the-newsletter-experience/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
