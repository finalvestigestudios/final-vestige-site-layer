# Dispatch R410 — executed QA, release and owner docket

**DRAFT / HOLD_UNSENT.** Stacked on [Dispatch R409 #2795](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2795), original six-issue [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), per-edition [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), owner [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). No production changes or subscriber contact.

## Native tests actually executed

- Original canonical campaign: Python **3.13.5**, `python -m unittest discover -s tests -p 'test_*.py' -v` run against all eight byte-identical source files from previous verified QA archive and rechecked against **current PR #175 HEAD d57ccdba3aee8f065e143e101c2945f4f3d01647** using GitHub's authoritative Git blob SHA. **6/6 PASS.** Canonical manifest and all six issues unchanged.
- R410 exact-source Node **22.16.0**, `node --test test_focus_gift_signal.cjs`, **27/27 PASS**. The two committed JavaScript files were independently fetched from the new GitHub branch and their exact blob hashes matched native tested files: `focus_gift_signal.cjs` **17379965d84b8770154f9cea98a20222aa562dd5**; `test_focus_gift_signal.cjs` **466b4893d7402b8bd58c27081cc55d8cc747fc7c**.
- R410 standalone static HTML review board: **Chromium, in-memory set_content** at seven viewport widths **320 / 360 / 390 / 768 / 1024 / 1440 / 1920 px**, one H1, no root horizontal overflow, no page JS errors, **7/7 PASS**. Two offline screenshot files 390 and 1440 px retained in local QA archive, not screenshots of Jetpack email or the live site. Exact board Git blob SHA **e47877d53c5ac88fd467dbb53350bd003568d437**.
- Test-correction transparency: first VM harness omitted global `MutationObserver`, yielding 18 test-environment errors; added the correct fake global. Next assertion expected `maybe-is-subscriber-later` not to match, but the source `/\bis-subscriber\b/` matches across hyphens; expectation corrected, **27/27 final pass**. Browser's `file://` URL was blocked by policy, so the static HTML bytes were loaded using `page.set_content`. First 320 px pass found a long-code-token overflow, corrected with `overflow-wrap:anywhere`, then all seven viewports passed. No concealed failing gate in the final source.
- This is **not** evidence of a real signup, external merchant permission, valid CAN-SPAM email footer, actual native WordPress email Preview, cross-client rendering or an actual Fieldbook welcome receipt.

## Read-only current state and release gates

- Authenticated WordPress newsletter status 2026-11-16 23:38 UTC: `subscriptions=true`, `site_can_send=true`, `email_new_posts_by_default=false`; last five post notifications `never_sent_opted_out`. Counters **total3 confirmed3 unconfirmed2** do not add to five unique recipients; follower counts **wpcom3 email0** describe distinct reporting categories. Eligible inbox count **UNKNOWN**.
- Welcome message contains the 52-page Fieldbook URL; no actual receipt/welcome-complete provider proof. Connected Gmail targeted searches found no affirmative product-specific merchant email permission, and no matched received new Dispatch welcome; a zero search hit is not proof of absence elsewhere.
- Official Hypnosis Live product/FAQ claims, Zen12 seller pages and WordPress preview/FTC requirements reviewed separately; merchant marketing does not prove Final Vestige partner status. Commercial Issues 03 Zen12 / 05 Total Focus remain **HOLD_MERCHANT**. Issue 04 **HOLD_COPY**. All six canonical issues **HOLD_UNSENT**. No affiliate link/price/refund claim activated.
- Actual FV commercial mailing address, functioning unsubscribe in a native Jetpack mail render, product-specific EMAIL permission, issued earning URL and live authorized buyer guides **UNVERIFIED**. No paid settlement or audited qualified-human session denominator; realized net revenue per 1,000 qualified sessions is **NOT COMPUTABLE**, never reported as zero.

## Owner-ready handoff

**OFFER → FUNNEL STEP → BLOCKER → CHANGE → PASS/FAIL PROOF → OWNER**

1. **Free Fieldbook → Grok social → Focus attempt → provider confirmed lead**: visible gift/URL query is client-only; map it as a UX hint and require authenticated, unsubscribed/suppressed reconciled confirmed provider record; **native 27/27 PASS, real provider acceptance UNKNOWN**; **Claude / Focus #129**.
2. **Dispatch → recipient → email**: unique eligible inbox count and genuine visual/email footer are missing; privately reconcile Jetpack recipients and capture a **non-sending** editor Preview with post email toggle OFF; **NOT EXECUTED**; **Dispatch / Founder**.
3. **Zen12 or Total Focus → vetted warm-up guide → settled commission**: named Inspire3 product-specific EMAIL approval/issued earning link/referred checkout/live approved guide missing; **HOLD_MERCHANT**; **Mind / Commerce #171**.
4. **Grok unique asset → qualified session → settled net revenue**: use existing TASK-008 conventions; Claude/analytics to join only appropriately consented provider/merchant evidence; **no real order/session proof available**; **Claude / Praxxis / #820**.

**Operational protections:** No WordPress posts or settings modified; no subscriber list exported or addressed, no test emails or live emails, no email schedule, no affiliate activation, no paid tools, no social posting, no PR merge. Homepage flagship PR #49 remains frozen, untouched. Founder must separately approve final campaign and every send/release.

