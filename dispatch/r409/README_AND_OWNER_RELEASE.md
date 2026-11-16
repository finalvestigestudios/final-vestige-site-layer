# Dispatch R409 — SKU-specific affiliate EMAIL authority and conversion gate

**DRAFT / HOLD_UNSENT / NO RELEASE AUTHORIZATION** · 2026-11-16

This is an additive audit layer for the exact six original issues in [master PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) and the separate per-edition gates in [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), stacked on latest [Dispatch PR #2791](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2791). Source of truth: [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129) and [revenue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Homepage flagship and frozen PR #49 are untouched.

## Commercial decision: choose ONE high-intent offer, not more newsletter volume

The provisional first audience is an *existing, lawfully confirmed* Fieldbook reader who voluntarily expresses interest in short meditation practice. The one product hypothesis is **Zen12**, but the proposed Issue 03 CTA to a vetted guide is still INACTIVE. Mind & Affiliate Studio, not Dispatch, owns the actual guide and commercial eligibility. Issue 05 reserves the second and final commercial placement for **Hypnosis Live Total Focus**, but is not activated, and its permission must be verified separately. Issues 01, 02, 04 and 06 remain editorial. No new issues or mass sends are queued.

**Proposed (not deployed) journey:** Grok's existing asset with unique asset_id → matched research page or /focus/ → provider-confirmed subscriber with once-only deduplication → verified 52-page Fieldbook welcome receipt → useful free practice → reader-selected evidence-led buying guide → permission-checked Issue 03 email with one relevant guide CTA → seller checkout with an independently issued earning link → independently settled commission, less refunds/fees. No blanket follow-up based on inferred health traits or hidden behavioral segments.

## Specific failure mode this sprint fixes

An Inspire3 catalog page, public Zen12 sales letter, publicly shared *Limitless Labs* swipe copy, merchant customer promotion, unrelated ClickBank account or approval for web traffic **does not establish named Final Vestige approval to promote Zen12 or Total Focus by EMAIL**. Nor does authorization for one product carry over to another. The offline validator enforces product-scoped provenance, channel-scoped partner permissions, fresh seller terms and separate footer/consent/preview witnesses; no public promo can substitute for private partner authority.

The eleven required product-specific evidence kinds are named affiliate acceptance, email-channel permission, issued product earning link, exact SKU terms, claim alignment, published vetted guide, native email Preview, FV mailing address, operational unsubscribe, provider consent eligibility and actual welcome receipt. Records must have an opaque non-identifying proof reference, source authority, product scope and dated review/expiry. **Metadata validation does not independently prove any of those documents or actions occurred.** All outcomes still say mail_allowed=false and HOLD_UNSENT, including the all-green synthetic fixture.

## Live WordPress and consent truth — read-only 2026-11-16 22:30 UTC

| Connected measurement | Observed | What it establishes |
|---|---|---|
| Jetpack newsletter / send capability | Enabled / technical can_send | Not approval or list permission |
| New post automatic emails | OFF | Preserve |
| Email format / sender / replies | full / Final Vestige Studios / no-reply | Subject and preheader still require native Preview |
| Newsletter total / confirmed / unconfirmed | 3 / 3 / 2 | **Nonadditive, overlapping categories** |
| WordPress.com / direct-email followers | 3 / 0 | Cannot infer unique inbox-eligible audience |
| Latest five post notifications | never_sent_opted_out | No proof of delivered campaign mail |
| Fieldbook welcome | Configured with 52-page PDF URL | Does not establish receipt or link use |
| Jetpack native Preview, FV address and unsubscribe | Not witnessed | Commercial sending blocked |
| Named product/channel affiliate approval and paid settlements | Not independently verified | Commercial sending blocked and revenue unknown |

Connected-mail search found promotional messages but no reliable Final Vestige-specific EMAIL approval. Failure to find a message does not prove no agreement exists elsewhere. Do not share subscriber identities or private merchant terms in GitHub.

## Product-specific buyer claim map (seller claims ≠ independent outcomes)

| Product | Exact vendor surfaces | Supported descriptive text | Must not say |
|---|---|---|---|
| **Zen12** | [Official description](https://zen12.com/about), [separate promo](https://zen12.com/secret/) | Seller describes 12 levels, four listening styles and 12-minute sessions; different promotional checkout pricing | No independently proven “12 minutes = one hour,” guaranteed mental effects, current price or promotion without the referred checkout |
| **Total Focus** | [Official SKU page](https://hypnosislive.com/mental-skills/total-focus) | Seller lists 33-minute / 47 MB MP3; separate observed captures show differing single and bundle price presentations | No guaranteed focus results, fabricated personal test or price certainty |
| **Total Focus refund** | [Official FAQ](https://hypnosislive.com/faq) alongside SKU page | Seller describes a 14-day satisfaction guarantee, **with a maximum of five refunded sessions per year** | No unconditional refund or unqualified “risk-free” wording |
| **Limitless Labs** | [Separate public affiliate offer](https://inspire3.com/ll/) | Has its own special approval and public email swipe resources | Does not grant Zen12 or Total Focus promotion permission |

## One step at a time: OFFER → FUNNEL → BLOCKER → CHANGE → PROOF → OWNER

| Offer / funnel | Blocker | Proposed change / experiment | Required PASS evidence | Owner |
|---|---|---|---|---|
| Zen12 / Issue03 → guide → paid commission | No named EMAIL permission, issued link, approved live guide or referred checkout | Once approved, one original email CTA to impartial guide, one proximate affiliate disclosure; no price promise | Authentic partner account & EMAIL rules for Zen12, vetted live guide, actual checkout, independent settlement | Mind/Commerce (guide), Dispatch (email) |
| Total Focus / Issue05 → guide | Different SKU, refund qualifications and price drift | Separate commercial track; only one direct relevant guide CTA | Separate SKU approval/email rules; refund and checkout witness | Mind/Commerce |
| Focus → confirmed subscriber → welcome | 3/3/2 vs 3/0 stats are nonadditive; receipt unknown | One confirmed_signup event only from authenticated, deduplicated provider transition, never browser query or download | Redacted provider eligibility record and authorized welcome/Fieldbook receipt witness | Claude/Focus |
| Dispatch → compliant inbox | No true Preview, mailing address or operational unsubscribe | Native WordPress *Preview email* only in permitted UI, not a Send test email | Actual sender, subject, preheader behavior, device layout, FV address, functioning opt-out and disclosure | Dispatch/Founder |
| Grok acquisition → settled revenue | No audited asset/session/order join | Use already approved creator asset IDs and existing measurement stack | 7/30-day qualified-human session audit + paid order/commission after refunds and fees | Grok/Praxxis, Claude analytics, Commerce settlements |

## Attribution contract — PROPOSAL ONLY, do not deploy tracking now

Social inbound uses the existing agreed utm_source=(actual platform), utm_medium=organic_social, utm_campaign=mind_pilot_2026_11, utm_content=(unique published Grok asset_id). Disclose attribution limits if the platform only has a profile link. Future permission-approved email uses utm_source=dispatch, utm_medium=email, utm_campaign=dispatch_pilot_2026_11, utm_content=issue03_zen12 or issue05_total_focus. No email address, subscriber ID, medical interest, private token or secret in UTMs. No duplicate GA script. Confirmed_signup is counted only on provider-authenticated transition plus lawful consent/suppression/deduplication. Email clicks, checkout starts and claimed signups are not sales. Revenue per 1,000 qualified-human sessions is **NOT_COMPUTABLE** until reliable settled sales, fees/refunds and a qualified session denominator are jointly available; no tiny-list A/B claims.

## Actual legal/email QA, distinct from offline HTML

The WordPress [2026-11-09 Preview documentation](https://wordpress.com/support/newsletter/email-appearance/) separates **Preview email** from **Send test email** and supports device views. WordPress [2026-11-13 sending guide](https://wordpress.com/support/newsletter/send-newsletter-emails/) says post title becomes the subject. A manuscript preheader line is **not proven** to appear as the inbox preheader; actual rendering must be checked. FTC [CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires truthful sender/subject, commercial disclosure, legitimate FV physical postal address and functional opt-out. The merchant's London/Delaware business address and WordPress/Automattic's sender address cannot substitute for FV's legal mailing address.

**No WordPress or subscription writes, subscriber contact, email/test email, social post, affiliate link activation, merge or spend. No use of homepage PR #49. Founder retains distinct final approval of exact content, audience, schedule and release.**
