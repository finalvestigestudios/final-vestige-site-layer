# R463 — exact-source and privacy-safe QA receipt

**Draft PR:** [#3086](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3086). Stacked on [#3081](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3081) exact `40f78500b9bcb803269d6480d2b762ffd7ad5f0e`. Head before adding this receipt: `0285044084ebfe3eacda88b3fdd5c29c07ee0dd2`. Canonical [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) immutable `d57ccdba3aee8f065e143e101c2945f4f3d01647`; #201 QA, #49 homepage untouched.

## What actually ran

1. **Exact original six Markdown files + manifest** independently fetched at canonical SHA using GitHub connector and all six **Python test conditions mirrored as V8 assertions**. **6/6 PASS**, with original blob hashes documented in issue #174. This is **NOT a native Python test run**; GitHub DNS fails in container. The original suite must still be run natively on checked-out exact head for final acceptance.
2. **Committed first five R463 new files** independently fetched from GitHub before creating PR and checked for subject/preheader consistency, one free CTA, actual source links, no tracked/merchant-buying URL, email-safe static markup, adjacent disclosure, four explicit stop placeholders, truthful 4:2, absent permission/settlement, incompatible subscriber counts and null revenue. **24/24 V8 structural assertions PASS**. Source blob hashes:
   - `ISSUE03_EVIDENCE_FIRST_OPTION.md` — `d567da5894f6d5cdb1466eae1ce515bac31893ba`
   - `ISSUE03_OFFLINE_REVIEW.html` — `7c085db1f83e2a28c4d7a617a382dfeeb2e7d66d`
   - `ISSUE03_OFFLINE_REVIEW.txt` — `c8c17db8af9f103a5c721d8fba821c0f141b6d4e`
   - `RELEASE_AND_SOURCE_LEDGER.json` — `f0be4f27a581e5dd5cf90b4798285f4dded6e052`
   - `R463_OWNER_RELEASE_DOCKET.md` — `f6f0e6f149b2e2483c0eb9bd98a45e463c20dda2`
3. **4/4 deliberately unsafe offline string mutations rejected**: remove commercial disclosure, replace postal placeholder with fabricated address, inject external script, falsify HOLD banner. This is **source-only QA**, not a browser or actual inbox rendering.
4. **28/28 native Python unittest checks PASS** on a **separate local prototype renderer and its local specimens** in `/mnt/data/dispatch_r463/`, including copy fidelity, link allowlist, footer stops, header newline injection, one CTA, language, mutation rejection and deterministic outputs. These local files are **not byte-identical** to the GitHub HTML/plaintext assets. Do not describe the 28 as exact committed-HEAD tests.
5. New source-only `dispatch/r463/test_release.cjs` was committed for portability and may be run with `node dispatch/r463/test_release.cjs` after checkout. **Native Node against exact committed HEAD NOT EXECUTED.**
6. WordPress authenticated **read-only** at **2026-11-19T04:33Z**: Newsletter `subscriptions=true`, new-post default OFF, full email; latest five post-email notices never sent; Stats Emails no rows; `total=3 confirmed=3` and **additional unconfirmed=2**; Stats Subscribers email3/Reader0, Stats Followers email0/Reader3 (partial=false). Never sum counts or infer independently verified human signup. Welcome configured but received receipt absent. Public /dispatch/ `modified=2026-11-18T20:29:41` and /focus/ `modified=2026-11-16T14:54:58` contain a publication-triggered email promise despite disabled default sending. Focus live no-repeat-signup instruction is already corrected. No subscriber identities exported or displayed.
7. Targeted Gmail found **2026-08-24 Refersion `Your affiliate account is pending`** and no later account-specific acceptance in searched mail; that is **not proof that the account is rejected**. Current official vendor pages: [Zen12 /about](https://zen12.com/about), [Zen12 /secret](https://zen12.com/secret/), [Zen12 packages](https://zen12.com/?no-popup=1), [Hypnosis Live FAQ](https://hypnosislive.com/faq), [specific SKU](https://hypnosislive.com/self-growth/be-more-centered). Product benefit, checkout price, special refund terms and marketing email rights still not authenticated for FV.
8. No genuine native Jetpack preview or inbox, publisher postal confirmation, unsubscribe verification, double-opt-in/welcome delivery, current direct PDF download witness, published official warm guide, account-issued affiliate URL, transaction/fee/refund reporting, live A/B, audience contact or spend.

## Required gate before any release

**All six original issues and R463 optional copy: HOLD_UNSENT.** Exactly four editorial / two commercial reserved. Founder review/explicit mailing approval remains required; acceptance requires actual WordPress Preview and rendered opt-out/postal, fresh consent verification and partner-specific EMAIL permission+approved offer route for Issues 03/05. No CMS writes, emails/test sends, schedule, new list, affiliate activation, PR merge, social posts or spending occurred. **Commercial KPI net settled revenue per 1,000 qualified-human sessions: NOT COMPUTABLE**, not 0.

## Release ownership

Dispatch #174: copy/transport. Focus #129 and Claude: consent, welcome, provider classifications, approved public promise. Mind #171: issued affiliate account/guide and sales-page claim clearance. Growth #820 / Grok / Praxxis: source-tagged qualified human sessions and paid settlements. Founder: postal address and final approval. Homepage #49 remains protected.
