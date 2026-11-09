# Dispatch R234 | Jetpack delivery constraint and subscriber-intent bridge
**November 9, 2026 — SOURCE ONLY / UNSENT / NOT APPROVED FOR PUBLICATION**

Parent: R233 PR #1752 @ `16e55ac70b8f1a52815c9c48de4ca528f9cea18c`; master Issue #174; merchant Issue #171; Focus Issue #129; conversion Issue #820. Frozen homepage PR #49 and original PR #175 are not edited.

## New P0 operational finding
The official Jetpack Newsletter guide (updated **November 4, 2026**) says that **Jetpack Newsletter emails subscribers when a new WordPress post is published; pages, custom post types and edits to published posts do not trigger a newsletter**. The editor has a *Preview email* function for unpublished posts even when **Send this post to subscribers** is OFF, but the *Send test email* function really does send a message. See https://jetpack.com/support/newsletter/ and https://wordpress.com/support/newsletter/send-newsletter-emails/ .

**Consequence:** A sequence of six free-floating email files is **not** an independently deployable six-email drip in the current Jetpack configuration. Do not claim that issue files can be dispatched as standalone transactional emails. Sending through the native mechanism is coupled to publishing a qualifying post; publishing is forbidden without the founder's separate approval. Drafting, reviewing and testing on disk or on GitHub are allowed. There is no requirement to buy a new service or create another list.

### Non-sending proof sequence (staged; not authorization)
1. SOURCE ONLY — existing issue files, preview HTML/plaintext and this evidence matrix; all marked HOLD.
2. **Only after separate permission to create a WordPress draft**: stage ONE future issue as an unpublished post (not a page), inspect editor type and **Send this post to subscribers = OFF**, use native Preview email *without* clicking Send test email or Publish. Record redacted desktop/mobile preview evidence and exact editor settings.
3. **Only after explicit separate permission for a test message**: use Jetpack's editor *Send test email* to a designated consenting recipient; inspect received MIME, sender identity, legal postal address, opt-out content and real rendering. This approval does NOT include publication or the actual subscriber list.
4. **Only after campaign-specific final founder approval**: select each intended publication, publication date, exact post/send controls, audience and content; prevent editorial posts elsewhere from auto-emailing. Native sends may depend on the publisher's chosen post workflow. Never turn on automatic new-post emails globally without approval.

All steps 2–4 are **UNPERFORMED**. Jetpack's `site_can_send=true` diagnoses capacity, not delivery or final consent. Existing five recent posts are `never_sent_opted_out`. No preview created inside WordPress, no draft post, no test email, no send and no schedule.

## New P0 conversion finding: 'twelve minutes' is not a shared buyer intent
The live `/focus/` page promises help **starting avoided tasks in a twelve-minute work block**. Zen12's exact `/hnp` seller page sells a **twelve-minute guided/audio meditation** and asserts that it provides the benefits of an hour of meditation. These are different actions with different desired outcomes. The coincidence of duration must NOT be used as evidence of a good product fit. Directly pitching meditation to every Fieldbook subscriber risks disappointing someone who joined for task-starting, an observation/hypothesis **not measured behavior or proven churn**.

**Audience-intent hypothesis (not individual profiling):** prioritize readers who voluntarily clicked a sourced Mind/meditation investigation or explicitly requested a buyer checklist; show readers who only expressed task-starting interest editorial help first. No segmentation/list changes are currently authorized or even known to be supported by this Jetpack site. Do not infer interests from named recipients, health traits, tracking pixels, or email opens. A free practice and a choice to skip the commercial guide must remain available.

The alternative 03 copy is deliberately an **unapproved replacement proposal** for review, not an overwrite of the six original manuscripts. It asks a skeptical buyer what to compare, without implying a Fieldbook work sprint equals audio meditation, without suggesting product efficacy, price, discount, endorsement or refund verification. Commercial disclosure appears beside one **inactive** guide CTA. Issue 05 remains a separate provisional commercial slot; the original six-issue allocation stays **4 editorial : 2 potential commercial**.

## Observed read-only source state, 2026-11-09 ~14:48 UTC
WordPress Jetpack newsletter: enabled, `email_new_posts_by_default=false`, `email_content_format=full`, `reply_to=no-reply`; welcome configured with the 52-page Focus Fieldbook. Counters **total=3 / confirmed=3 / unconfirmed requests=2 / suppressed=0** are nonadditive and do not prove three email-eligible recipients; WordPress.com followers **3** and email-only followers **0** from an earlier independent count also cannot be summed. Five recent posts show no sends. No final Fieldbook welcome receipt or compliant actual delivered message verified.

Connected Gmail search for named Final Vestige partner email promotion permission or the Fieldbook welcome produced **no positive proof**; other merchant promotional mail is not authorization. Mind #171 latest handoff still lists affiliate account acceptance, EMAIL promotion permission, merchant-issued earning URLs and LIVE approved buyer guides as absent. Do not use unverified mail or inferred clicks to claim commercial acceptance, lead generation or paid sales.

## Hard gates and owner priorities
| Offer → funnel step | Blocker | Proposed change / experiment | PASS/FAIL evidence | Owner |
|---|---|---|---|---|
| Zen12 → qualified buyer | Work-start vs meditation **intent mismatch** | Invite only genuinely interested readers to impartial guide after authorization; preserve free alternative | **SOURCE-ONLY hypothesis**; no cohort data | Dispatch / Mind |
| Dispatch drafts → real delivery | Jetpack publishes POST to send email; no approved CMS publishing | Review post-bound preview workflow; do not create post | **DOCS VERIFIED, NATIVE PREVIEW NOT TESTED** | Dispatch / Claude |
| Zen12 guide → eligible earning link | Partner EMAIL rights, issued URL, live reviewed guide absent | Mind verifies merchant account and partner-specific email terms | **FAIL / HARD_HOLD** | Mind Studio |
| Existing subscriber → welcome | Actual delivery, postal address, unsubscribe unknown | Consent-preserving received-MIME inspection **after separate approval** | **NOT TESTED** | Dispatch / Site QA |
| Focus → confirmed lead | Summary counters ambiguous and URL gift not confirmation | Validate provider-confirmed email subscription event once, deduplicate in aggregate | **NOT VERIFIED** | Claude / Focus |
| Paid buyer → realized net | No supported settled order/commission or qualified sessions | 7/30-day settlement and refund reconciliation; KPI net revenue/1,000 qualified human sessions | **NOT COMPUTABLE** | Commerce / Praxxis |

## Release blockers
**ALL SIX HOLD_UNSENT.** #03/#05 also **HOLD_MERCHANT**. No publish, email, test email, opt-in, list import, settings change, commerce activation, Grok social post, new measurement pixel or spend. Founder retains final content/publication/sending authority.

References: https://jetpack.com/support/newsletter/ (updated Nov 4, 2026); https://wordpress.com/support/newsletter/send-newsletter-emails/ ; https://finalvestige.com/focus/ ; https://zen12.com/hnp ; https://hypnosislive.com/mental-skills/total-focus ; https://hypnosislive.com/faq ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174 ; https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171 .
