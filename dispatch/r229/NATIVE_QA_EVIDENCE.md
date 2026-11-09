# R229 native independent test evidence — 2026-11-09 10:14 UTC

**Parent (unchanged) R228 commit:** `ed38970572ce17f0f40b30dafbdc91e809daf5ba`; draft master PR #175 and Issue #174, readiness PR #201 retained. Isolated branch `dispatch-r229-native-provider-email-eligibility-gate-20261109`.

## Executed, native and reproducible
Local Python native command:
```
python -I -m unittest discover -s dispatch_r229/tests -v
```
**Result: Ran 32 tests in 0.001s. OK (32/32 passed), Python 3.13**.

- Native-tested module exact Git blob: `0fdde50970a251b1c13257839640a851a130aeff` == GitHub `dispatch/r229/eligibility_guard.py`.
- Native-tested tests exact Git blob: `13f4ff8054afedbbb25f7096949ca67ea24daff4` == GitHub `dispatch/r229/tests/test_eligibility_guard.py`.
- Negative cases: duplicate order IDs, missing authoritative settlement, non-USD currency, malformed/NaN revenue, fake provider confirmation, Reader-only and bounced accounts, duplicate signup, absent Dispatch consent, unverified attribution, PII fields, all-true fake attestations still cannot authorize a send.
- The signed tests run only on synthetic fixtures; no live paid transaction, subscriber, SMTP or WordPress settings touched.

Original PR #175 Python suite is committed but **was NOT run natively** from a complete exact-head checkout because this runtime cannot resolve private github.com in its shell. Independent V8 logic assertions reproducing its six checks against exact current SHA `ed38970572ce17f0f40b30dafbdc91e809daf5ba` passed **6/6**; these are **not** native Python execution or hosted CI. Keep this limitation explicit.

## Current read-only upstream evidence (2026-11-09 10:03 UTC)
Authenticated WordPress Newsletter `total=3 / confirmed=3 / unconfirmed=2 / suppressed=0`; follower API separately `wpcom=3 / email_only=0`; automatic new-post emails OFF, full-content, configured Fieldbook welcome, five recent posts `never_sent_opted_out`. The provider has NOT furnished count grouped by **Email subscription status=Subscribed**. Neither email-only=0 nor confirmed=3 is authoritative email-recipient eligibility.
Public routes `/dispatch/` (page 523), `/focus/` (1579), Editorial Standards (17), PDF (1737). Source observation: `/focus/` repeats "sign up again" in app-browser copy, a repeat-attempt issue already assigned to PR #1711. Dynamic Subscribe block appears as fallback anchor in WordPress editor API; do NOT treat as proof that signed-out public form fails. Actual user/browser and provider status checks not conducted.

Gmail search did not establish FV named Inspire3 EMAIL rights or received final welcome. Mind final R238 owner handoff #1720 commit `a5dbabc2ffb613b9137b18d8d53da04f193539db` explicitly retains commercial hold.

## Hard constraints
**ALL SIX HOLD_UNSENT; #03 and #05 HOLD_MERCHANT.** No send, test email, WordPress write, recipient export, signup import, active earning URL, live CTA, merchant account mutation, paywall, tracking script, paid spend, Grok assets, PR #49 edit or site deployment.

Native email MIME preview, final Fieldbook receipt, legally valid FV postal mailing address, actual working unsubscribe, account-issued partner earning URLs, explicit merchant EMAIL permission, published buyer guides, real customer purchases/settlements/refunds and genuine qualified session data remain **not verified**. Net revenue per 1,000 qualified human sessions **NOT COMPUTABLE**, not zero.
