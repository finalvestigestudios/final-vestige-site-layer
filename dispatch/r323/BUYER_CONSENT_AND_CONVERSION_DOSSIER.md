# R323 — Two lists are not one lead: Dispatch commercial conversion and consent review
**2026-11-13 06:31 UTC authenticated configuration; UNSENT research package.**
Owner: Dispatch #174; partner/guide eligibility: Mind #171; Focus provider engineering: #129; business truth: #820. Master draft PR #175 at d57ccdba3aee8f065e143e101c2945f4f3d01647. Companion gated PR #201. Previous confirmation correction PR #2302. Mind research and seller sample consent proof PR #2306.

## New verified commercial wrinkle
The official Zen12 free audio page https://zen12.com/gift explicitly states "You will receive our newsletter." Its opt-in is a **Zen12/Inspire3 merchant relationship**. Final Vestige's /focus/ and /dispatch/ forms belong to the **existing WordPress.com/Jetpack Dispatch relationship**. These are NOT the same list or consent. A publisher should not describe Zen12's gift as merely a neutral audio download, route unconsented Dispatch readers to an unexpected seller opt-in without warning, or count seller subscribers as publisher leads. This is substantiated by seller-page wording, NOT a claim that any particular user opted in or that merchant newsletter was delivered.

### Four separate states (never collapse)
1. **FV site signup interaction** (input/button/query state): can be observed only as an attempt. /focus/ can reveal download panel based on query input: not consent evidence.
2. **FV new active, email-eligible Dispatch enrollment**: needs private, authenticated provider-origin event. WordPress describes email-link confirmation for nonaccount visitors and immediate active enrollment for existing WordPress.com accounts. Both require consent and new-site enrollment evidence, not first-seen active snapshot. Do not expose email addresses, use opaque keys and event references.
3. **Merchant free-MP3 opt-in**: seller says own newsletter included. Keep separate; no data import, list joins, syncing, or default attribution into FV.
4. **Independently settled paid conversion**: seller/processor evidence that a paid order resulted in a commission, adjusted for refunds and fees. Neither seller free gift, affiliate click nor checkout start is a sale.

## Exact merchant claim map — checked 2026-11-13 UTC
| Topic | Seller's public page | What FV can responsibly say | Release implication |
| --- | --- | --- | --- |
| Separate free-gift consent | https://zen12.com/gift | Free-MP3 page says visitors will receive seller newsletter | Warn beside any mention; no default endorsement or live CTA |
| Beginner | https://zen12.com/ | First six levels, 24 MP3s | Not same as full Premium |
| Premium | https://zen12.com/ | All 12 levels, 48 MP3s | Exact edition for proposed buyer guide |
| Advanced | https://zen12.com/ | Later six levels, 24 MP3s | Not full program despite name |
| Hour equivalence | https://zen12.com/ | Advertising promise; not independently validated product outcome | Don't claim proven, no comparative data fabricated |
| Meditation studies | https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety | Reviews broader techniques with caveats and safety issues, not Zen12 trials | Context, never product proof |
| Total Focus reserve issue 05 | https://hypnosislive.com/mental-skills/total-focus | Seller shows 33 min, 47 MB; benefits seller-promised, checkout/returns unverified | Keep reserve, no approved email promo |
| Affiliate authority | https://affiliates.inspire3.com/ | Public portal explains paid referral program; does not verify account rights | Partner proof HOLD |
| Final Vestige commercial duties | https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business | Truthful subjects, postal address, functional opt-out, sender identity and applicable ad disclosure | No message send until native witness |
| Affiliate endorsement disclosure | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking | Actual material commission connection requires clear and conspicuous disclosure | Near guide offer; repeat beside outbound earning link |

**Important drift caution:** seller displayed product prices and money-back language are not verified final checkout/contract terms. Do not anchor emails to a dollar or guaranteed refund. Zen12's general meditation research link does not close the scientific-efficacy gap. No approved merchant swipe/creative or email-channel authorization has been produced by the public site.

## Candidate editorial angle / conversion logic
High-intent audience: a Dispatch reader already practicing with the Fieldbook who wants to evaluate whether to pay for a short guided audio. One relevant **future** CTA: a verified, accessible, independent Zen12 Premium buyer guide (not a merchant opt-in). The guide, when approved, should compare full Premium to free practice, explain tier differences, distinguish marketing claims from independent evidence, and warn clearly if the seller's optional free sample adds seller newsletter emails. Downstream an earning link can be disclosed near the link only after **account-specific email rights** and partner URL terms are authenticated by Mind/Commerce. Never require subscription to access a substantive independent guide.

Do not chase A/B results from 3 total / 3 confirmed / 2 unconfirmed overlapping counts. Do not use sender-level counts as confirmed email-eligible recipients. A person may be a Reader follower, paused or otherwise unable to receive email. The last five WordPress send records are `never_sent_opted_out`; don't turn that into a lifetime zero-sends claim.

## OFFER → FUNNEL → BLOCKER → CHANGE → PASS/FAIL → OWNER
| Offer | Step | Blocker | Change / experiment | Current proof and verdict | Owner |
| --- | --- | --- | --- | --- | --- |
| Zen12 Premium | Intro to exact offer | Merchant sample collects seller newsletter, email rights unknown | R323 consent-boundary editorial guide candidate, inactive CTA; verify permitted email channel and approval | Source verified; earning rights **FAIL/HOLD** | Mind + Commerce (#171) |
| Zen12 Premium | Guide to paid checkout | No approved live warm-up guide, partner link, permitted final pricing/refunds | Publish only after founder approval and rights review, independently verify endpoint on mobile | Not-live guide **HOLD** | Mind + Claude |
| Focus Fieldbook | Visitor to Dispatch subscriber | Query state/download !== newly consented eligible subscriber | Provider event contract supports email-link and WP-account immediate site enrollment; dedupe identity | Synthetic logic test, authentic events **MISSING** | Claude/Focus (#129) |
| Dispatch 03 | HTML/text to recipient inbox | No real native inbox, final FV mailing address, unsub witness | Founder-approved *non-sending* preview workflow first; actual received email only with separate approval | Offline assets **BUILT**, native evidence **FAIL/HOLD** | Dispatch/Founder (#174) |
| Grok asset | Human visit and qualified lead | First-party session join and verified asset id unavailable | Preserve asset_id/utm_campaign at session and landing; assign lead only with authenticated provider-origin join | No real session evidence **UNKNOWN** | Grok/Praxxis/Claude (#820) |
| Merchant | Click to settled sale | No merchant settled conversion/refund/fee report | Match stable opaque campaign/offer IDs with partner paid settlement; 7/30 day cohorts | Revenue/1,000 **NOT COMPUTABLE** | Commerce/Claude |

## Definition and experiment for the conversion hinge
Use **exactly one** `confirmed_signup` semantic event, only on trustworthy newly active + eligible Dispatch provider event, deduplicated by site + opaque identity + enrollment event. Retain a separate `signup_attempt` counter, separate `fieldbook_download` count, separate `merchant_sample_optin` (only if merchant independently reports; do not track people on seller pages), `affiliate_outbound_click`, and `settled_paid_order`. No new analytics script; Claude maps existing permitted instrumentation only, and no raw email addresses go to analytics.

Attribution convention for eventual approved emails: `utm_source=dispatch&utm_medium=email&utm_campaign=fv_dispatch_pilot_2026&utm_content=issue03_zen12_premium`. The email click should resolve to the **live approved first-party guide**, not directly to Zen12. Maintain a server-side or otherwise trusted first-party join with original Grok `asset_id` and its `utm_campaign`; do NOT infer a conversion from matching browser-supplied UTMs alone. A refund or fee reduces realized net revenue when reconciled.

Report only if source data exists: qualified-human sessions; verified eligible new leads; distinct paid orders/customers; settled gross, refunds, fees, realized net; paid conversion rate, lead-to-customer rate, and `1000 * net / qualified_human_sessions`. Use 7-day and 30-day cohorts with small-N context. If denominator or settlement provenance missing, return **N/A** (not $0). This repo's `gate.cjs` is a read-only synthetic proof contract and does not authenticate live records.

## No-sending / no-production policy
All original six emails remain `HOLD_UNSENT`, #03/#05 separately `HOLD_MERCHANT`. This alternate #03 is **NOT_ADOPTED** and requires founder editorial selection, then all native email, legal, partner, and commerce approvals. No source files under original /issues/, /focus/, /dispatch/, frozen homepage #49, merchant tracking, settings, subscriber list, or live website changed.
