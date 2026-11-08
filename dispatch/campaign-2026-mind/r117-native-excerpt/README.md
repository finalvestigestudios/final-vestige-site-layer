# Dispatch R117 — Native Post Excerpt conversion contract (DRAFT / NO SEND)

**Ownership:** Dispatch #174; original six-mail master #175 (SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`); prior per-issue gate #201; full-body offline preview PR #957. Mind & Affiliate #171 owns merchant permission/guide eligibility; Focus #129 consent; #820 attribution. Frozen homepage PR #49 untouched.

## New issue uncovered: native email transport is not the R116 HTML preview

On **November 4, 2026 ~16:37 UTC**, an authenticated WordPress check found Newsletter ON, new-post automatic emailing OFF, **excerpt** delivery, sender Final Vestige, no-reply, the 52-page Fieldbook welcome *configured*, and five post notifications marked `never_sent_opted_out`. Reported subscribers: total=2, confirmed=2, unconfirmed=2; these figures must not be added together. Jetpack email followers=0 vs WordPress.com followers=2 has a different definition; actual reachable recipients and welcome receipt remain **UNKNOWN**.

[Jetpack's official guidance](https://jetpack.com/support/newsletter/) says newsletter notification email is tied to **publishing a new post**. Updating a published post or page does not send a new issue. Therefore the published `/focus/` and `/dispatch/` pages cannot serve as new issue transports; source-authored HTML templates, custom preheaders and six long Markdown letters do not themselves describe native inbox output. Individual publication + send controls require the founder's separate final approval. **No posts, pages, settings, subscriber records, or messages were changed.**

Official docs disagree about the auto-generated excerpt threshold: [WordPress.com settings](https://wordpress.com/support/newsletter-settings/) says **55 words** when no custom Post Excerpt exists; [Jetpack customization, updated November 4](https://jetpack.com/support/newsletter/customize-the-newsletter-experience/) says **350 characters** in its context. They agree that an **explicit Post Excerpt** is a safer control. We cannot pick one truncation rule as authoritative for FV without a genuine native editor preview. We propose six <=320-character excerpts, but have **NOT obtained the actual rendered editor Preview Email or a received email**. The native inbox preheader customization is also unverified.

## Proposed subscriber path, not a send

These six candidate excerpts are in `excerpt_contract.json`; none overrides the master manuscript. The expected action in an excerpt-mode email is **WordPress's native read-full-post link**. The full issue, once separately approved and eventually published, could then have a single first-party investigative CTA. Commercial issues #03 and #05 would link from full issue to separately vetted **first-party guide** (not a direct unapproved earning link). Both excerpts disclose possible commission **before the native read-through**. They include no active merchant links.

The allocation remains **four editorial (#01/02/04/06) and two commercial-reserved (#03 Zen12/#05 Total Focus)**. Issue #04's original subject “Fourteen seconds” is **NOT source cleared**; alternate copy is proposed, not substituted. Issue #06 proposes a direct, verified Fieldbook download for existing subscribers, not another forced /focus/ signup loop. Welcome/Fieldbook delivery and direct PDF access are unverified.

The official [Zen12 seller page](https://zen12.com/hnp) describes twelve levels, 48 MP3s and makes an unverified one-hour/equal-twelve-minutes claim; [an additional promotion](https://zen12.com/secret/) has variant terms. [Hypnosis Live Total Focus](https://hypnosislive.com/mental-skills/total-focus) describes 33 min / 47 MB, seller claims and dynamic promotional pricing. No Final Vestige-specific affiliate email permission, authorized link/creative, safe purchaser data rights, buyer guide, approved price or independent product efficacy is established. **One research candidate is NOT one authorized paid offer.**

## Conversion-first chain and actual KPI

Grok's immutable asset_id + approved UTMs → qualified topic-matched visitor → optional Focus → one consented authoritative native `confirmed_signup` transition (de-duplicated, no reader-only or unconfirmed count) → genuine Fieldbook delivery → evidence-first editorial → independently eligible first-party guide → optional authorized merchant click → **independently reported paid order** → refund/fees → realized net revenue. Email CTA tagging, if approved by Claude/#820, uses `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue_XX`; no email, subscriber ID or personal data in URLs. Grok asset source remains its separate original campaign context, not presumed last-click revenue credit. A merchant click is never counted as revenue.

**Primary KPI**: verified realized net revenue per 1,000 qualified human sessions for documented 7/30-day cohorts, only when both actual qualifying sessions and authoritative paid order/refund/fee records exist. Otherwise **N/A**; do not replace missing data with zero or generate fictional A/B significance from two subscribers.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Fieldbook → legitimate confirmed lead | Email eligibility & opt-in not independently reconciled | Native WP status filter, no list export | **UNKNOWN:** 2 total/2 confirmed/2 pending are nonadditive | Dispatch + Claude |
| Lead → welcome/PDF | Only configured welcome known | Privately inspect authorized received welcome and direct PDF page count | **HOLD:** no received-email proof | Dispatch QA |
| Newsletter → first-party article | Excerpt mode hides original full CTA/copy; post-only transport | Review explicit Post Excerpt in genuine native editor Preview Email | **HOLD:** offline is not transport proof | Dispatch + Claude |
| Zen12 → buyer guide → customer | No partner email authorization, live guide, or link | Mind owner supplies written permission/accepted terms + factual guide | **HOLD_MERCHANT**, zero verified earning links | Mind #171 |
| Commercial email → compliant inbox | FV physical postal, actual footer, unsubscribe action unresolved | Inspect real compliant native preview + authorized opt-out evidence | **HOLD:** vendor or Automattic address insufficient | Founder + QA |
| Actual buyer → net revenue | Sales/reconciliation source unavailable | Authenticate Payhip FV product or affiliate orders, net fees/refunds, source mapping | **N/A**, not zero | Claude commerce / #820 |

[FTC CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires truthful subjects, sender identity, valid **publisher** postal address, conspicuous promotional disclosure when applicable, functional opt-out and prompt suppression. A third-party template/footer does not by itself satisfy publisher compliance.

## QA / no-send reproduction

`python -I -m unittest discover -s dispatch/campaign-2026-mind/r117-native-excerpt/tests -v`

`python dispatch/campaign-2026-mind/r117-native-excerpt/verify_excerpt_contract.py --preview /tmp/fv-r117-static.html`

The Python script is a **no-network**, read-only release validator and generator of an **offline static accessible preview**; it has **no WordPress, SMTP, mailing, tracking, import, payment or affiliate activation code**. Its 18 native-Python adversarial tests were run on a local matching worktree, including mutation tests for fake approval, invalid 4:2 mix, missing close-to-CTA disclosures, seller link activation, PII, legal flags, Apollo subject, and signup loop. These local tests do not establish actual Jetpack delivery or hosted CI. A later independent source/content check must verify the exact committed blobs.

**Release decision:** all six **HOLD_UNSENT**; #03/#05 additional **HOLD_MERCHANT**. Founder approved draft development, not final creative/send/recipient schedule, any live settings changes, test messages, merchant links, or publishing. The first successful conversion milestone is a rights-cleared, independently verifiable *paid order*, not more drafts, opens or visits.
