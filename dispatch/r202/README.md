# Dispatch R202 — consent-state ambiguity and offer-specific original review

**STATUS: DRAFT, UNSENT, NO PRODUCTION WRITES.** This branch stacks on [R201 PR #1532](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1532) at SHA `78efad348bc55b5c8915e17851632adadddb7288`. Master six-issue [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), per-edition [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), homepage frozen PR #49 and Mind ownership remain untouched.

## What materially changed
- A **code-derived reproduction** of the real /focus/ page's five-value allow/block query gate shows any other nonempty `?subscribe=` value can reveal the download panel. That download visibility does *not* constitute an email-confirmed subscriber and must not become `confirmed_signup`.
- A conservative parser distinguishes WordPress REST Subscribe block anchor output from actual public browser widget behavior; we do **not** assert the widget is nonfunctional. The site's /dispatch/ REST page similarly renders a fallback anchor.
- A specific, ready-to-review **nonpublishing engineering correction plan** tells Claude how to separate downloadable Fieldbook UX from provider-confirmed consent, with structured negative cases.
- One **optional, original issue #03** HTML + plaintext reviewer is source-grounded in William James (1890), official NCCIH/AHRQ limitations and the exact seller Zen12 Premium offering. The subject is honest, one promotional CTA is deliberately inactive, and affiliate disclosure is adjacent. No price or unverified efficacy/reimbursement guarantee is promoted. The original issue #03 is NOT replaced.
- A six-issue funnel redline, source-permissions decision, dated provider facts and explicit negative release checklist improve business readiness rather than merely adding another newsletter.

## Executed QA
Source files re-fetched from committed GitHub, CJS executed with V8/CommonJS-compatible shim: **40/40 test/assertion cases PASS** (focus proof and negative-variant tests + 12 static issue HTML/plaintext checks). This is **NOT a native Node.js run, browser HTML QA, WordPress email preview or MIME test**. Original canonical PR #175 Python suite independently rerun in native Python locally against byte-identical archived source: **6/6 PASS**; original test+manifest blob hashes verified against live GitHub #175 head. No metrics invented or subscribed customers asserted.

## Exact remaining RELEASE blockers
1. **Focus/Dispatch subscriber eligibility:** provider-filtered `Email subscription = Subscribed` deduplicated count and authoritative consent transitions (Claude/Dispatch). Counters 3/3/2 are not additive or reachable-audience proof.
2. **Welcome delivery:** authorized received email + download verification missing (Dispatch); existing Oct 25 confirmation is NOT a welcome.
3. **Sender legal footer:** valid Final Vestige physical mailing address, actual delivered/rendered Jetpack unsubscribe and functioning opt-out, native email subject/preheader inspection (Dispatch/Site QA). The Automattic or Inspire3 street addresses may not be substituted for the publisher.
4. **Merchant rights:** named Final Vestige account acceptance, explicit **email** channel permission, issued earning link, approved creative, live independently vetted buyer guide, seller checkout/refund review (Mind & Affiliate Studio).
5. **Paid conversions:** independently settled merchant orders/commissions, verified fees/refunds and qualified human sessions for 7/30-day net revenue per 1,000. No inference from views, clicks, or empty transaction logs (Commerce/Praxxis).
6. **Final release:** founder approval of specific issue, actual eligible recipients, date/time and authorization for any test email or publication.

**Source-of-truth threads:** [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Grok remains video/distribution owner through TASK-008, Claude website and analytics production owner. No Grok task queue changes or paid products created.

### Safety invariant
No new email platform, list, spending, subscriber identification, email send, test send, scheduling, WordPress page edit/publish, real tracking script, published earning link, merchant contact or homepage change occurred. All six remain `HOLD_UNSENT`, 03/05 `HOLD_MERCHANT`.
