# Dispatch R292 — actual inbox evidence, offer permissions and conversion release

**REVIEW ONLY — no WordPress changes, no email sends, no test sends, no subscriber exports, no new platform, no expenses.** Stacked on Dispatch R291 draft PR #2112. Original six manuscripts in PR #175 and independent gates in #201 are unchanged. Homepage frozen PR #49 untouched.

## What is new and materially different

Older Dispatch reviewer assets proved offline typography, source text, and a fail-closed editorial ratio. They **did not** authenticate a genuine Jetpack-rendered or received email. This sprint supplies a versioned, checkable **capture-provenance contract** and 32 synthetic negative-case regression checks that distinguish (1) an author-produced HTML specimen, (2) a native editor preview, and (3) an actual received MIME. They cannot be substituted for one another.

The offline auditor always returns HOLD_UNSENT regardless of test success. It never reads subscriber addresses or sends. Actual copyright-safe email capture may be examined only with separate founder authorization; do not commit inbox headers, identifiable recipients, tokens, postal business address before it is publicly approved, or the real message itself to this branch.

## Fresh read-only observations 2026-11-12 00:40 UTC

Jetpack subscriptions on, can-send capability true, automatic new-post email off, full content, no-reply sender, 52-page Fieldbook welcome **configured, not observed delivered**. Counts: diagnostic total **3**, confirmed **3**, unconfirmed requests **2**, suppressed **0**; WordPress Reader followers **3**, email followers **0**. These are different provider populations; actual eligible email recipients **UNKNOWN**. Last five inspected posts have never_sent_opted_out; this does not establish zero lifetime sends.

**No confirmed FV publisher affiliate email marketing permission, earning URL, qualifying live guide, verified merchant settlement, legal publisher postal address or real received unsubscribe.** Connected Gmail targeted searches for Welcome to The Dispatch, Fieldbook and merchant partner approval did not establish them; absence of matching mail is not proof of global nonexistence.

## How to independently reproduce offline

`node dispatch/r292/test_release_gate.cjs` (32 synthetic negative-case tests expected). For the current read-only evidence, `const {audit}=require('./dispatch/r292/release_gate.cjs'); const e=require('./dispatch/r292/observed-evidence.json'); console.log(audit(e));` returns HOLD_UNSENT. Node tests are synthetics, **not delivery tests**.

Original PR #175 on its exact unchanged SHA d57ccdba3aee8f065e143e101c2945f4f3d01647: native Python `python -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_*.py' -v` passed **6/6** this run against an earlier R288 byte-verified local archive, with GitHub current test SHA `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`. No claim that local archives represent new work.

The R292 32/32 tests ran against exact GitHub file bytes in an isolated V8 Node-like shim; **native Node / GitHub CI not claimed passed** until independently run.

## Review order and authority

1. Claude / Focus: private provider confirmation lifecycle, suppressions, no false UI-based signup, prove one aggregate confirmed_signup without exposing subscriber identity.
2. Dispatch / founder: authenticate physical publisher address, genuine no-send Jetpack preview via editor, then *separately authorized* mailbox test and unsubscribe; editor preview is not a received email.
3. Mind / Commerce: authenticate Inspire3 account email-channel marketing acceptance, issued earning links, published guide and product current offer/terms; Issues 03 and 05 HOLD_MERCHANT.
4. Commerce: independently report paid orders, eligible settled commissions, refunds, fees, qualified sessions for 7/30-day cohorts; net per 1000 is NOT_COMPUTABLE until data exists.
5. Founder alone: approve exact issue copy, audience, delivery method/date and send after gates. `site_can_send=true` is capability, never authorization.

References: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174 ; https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171 ; https://wordpress.com/support/newsletter/email-appearance/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
