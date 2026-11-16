# R395 post-commit evidence — independent QA, read-only; all issues HOLD

## Exact authoring branch / Git blobs
Branch `dispatch-r395-cohort-attribution-integrity-20261115` created from R394 [PR #2709](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2709) HEAD `4df40dad38d770a34f5d07405b6c78c17710ec50`. No originals edited. [Campaign #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), [per-issue #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), all six offline specimens [#2703](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2703) and homepage frozen #49 unchanged.

- `dispatch/r395/cohort_guard.mjs` Git blob **`dccb391405498a4059595d10debeaecf850912d9`**.
- `dispatch/r395/cohort_guard.test.mjs` Git blob **`f122019e52278aeb0e1845756a8145c72194a07e`**.
- `dispatch/r395/REVIEW_BOARD.html` Git blob **`278842ed1dfac1f61d59a18e9f12fe0d3db4a4b5`**.
- `dispatch/r395/PROVIDER_SNAPSHOT_REDACTED.json` Git blob **`3d638b1e1829419397d9e3b0f79ddfe7e7cd5c7d`**.
- Five other source and decision files: README; consent/cohort contract; native preview/legal runbook; merchant/CTA decisions; this post-commit evidence.

## Actual native execution
Native runner executed in current isolated container: **Node v22.16.0**, command:
```sh
node --test /mnt/data/fv_dispatch_r395/cohort_guard.test.mjs
git hash-object /mnt/data/fv_dispatch_r395/cohort_guard.mjs /mnt/data/fv_dispatch_r395/cohort_guard.test.mjs
```
**31/31 PASS, 0 FAIL, 0 SKIP**. Both locally tested files have SHA-1 Git blob IDs identical to the two files freshly fetched from the GitHub branch; this establishes **byte-identical native execution** rather than V8 test-callback imitation. All test events, social assets, sessions, customers and dollar values were **synthetic fixtures only**. This does not assert a real FV purchase.

Coverage includes 7/30 window mismatch, audit input missing, identity/consent missing, seller EMAIL permissions false, unrelated global merchant commission, bot/pageview denominator, duplicate or conflicting settlement rows, duplicate order counted once with adjustment records, refund and fee subtraction, negative net, unrecognized checkout/not settled, after-as-of settlements, private email/IP rejection and permanent `SEND_ENABLED=false`.

The original #175 Python suite is fully committed and was read at the exact immutable #175 source this run, but **was not re-executed natively in R395**. It was previously executed in another sprint. This release does not claim original Python current-head native execution.

## Other static, post-commit checks
Re-fetched exact GitHub HTML/JSON and JS blobs. **19/19 static assertions passed**, including accessible HTML language, viewport, heading, real table headers, focus-visible styling, six issue IDs and all HOLD statuses, no scripts or signup form, no active merchant link, no addresses, WordPress auto-send remains false, recipient eligibility null and merchant named approval false. These are source assertions only. **No actual Chromium browser render or genuine WordPress Jetpack native email preview/received-message MIME** was tested.

## Confirmed source-of-truth, 2026-11-16 05:32 UTC
Authenticated WordPress: newsletter ON and technically sendable, automatic new-post newsletter emails OFF, `email_content_format=full`, reply-to `no-reply`, existing 52-page Fieldbook welcome configured, most recent five posts `never_sent_opted_out`. Jetpack 3 total / 3 confirmed / 2 unconfirmed **not additive**; WordPress.com follower 3 / direct email follower 0; unique email-reachable inbox count UNKNOWN. Published `/dispatch/` and `/focus/` and Editorial Standards verified read-only. Connected Gmail searched after 10/25 and found NO matching received Fieldbook welcome. Oct 25 confirmation is not final welcome. No relevant named FV affiliate EMAIL acceptance found in targeted Gmail searches; this is **absence in searched account**, not proof no authorization anywhere.

Official seller Zen12 https://zen12.com/about reports 12 levels and four listening styles, seller efficacy claims **not proven**. Public Inspire3 email swipe https://inspire3.com/ll/ is **Limitless Labs**, which requires approval; not Zen12 or Total Focus permission. Mind R414 https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2710 keeps specific SKU, EMAIL-channel permission, issued earning link, published pre-sell guide and referred checkout unverified. FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business and native WordPress https://wordpress.com/support/newsletter/email-appearance/ were checked Nov 15/16.

## Integrity gap corrected
R394 demanded audited sessions plus merchant settlement but did not bind those data to **the same 7/30-day cohort and real social asset**. It also dropped conflicts when settlement IDs were duplicated with different refund cents. In R395, **unmatched social/campaign/time joins and duplicate conflicts now fail closed**, with 31 native regression cases including negative controls. Fake commercial attribution is now harder to produce. This is a source-only control and needs real independent audit inputs before any operating or reporting decision.

## Launch and revenue status
Every original issue remains **HOLD_UNSENT**, Issues 03 and 05 further **HOLD_MERCHANT**, Issue 04 **HOLD_COPY**. The two disabled buyer-guide destinations remain disabled; 4 editorial / 2 commercial issue allocation is unchanged. No email/test email, import, newsletter setting/page change, CMS publication, paid program, link activation, social post, PR merge or founder-final campaign approval occurred. The physical publisher postal address, real rendered unsubscribe, actual Fieldbook receipt, native Jetpack preview, filtered receiving-inbox count, named product-specific email rights and settled affiliate commissions all remain unverified.

Actual FV net USD per 1,000 qualified human sessions in both 7-day and 30-day periods: **NOT_COMPUTABLE** (no actual audited denominator or independently reconciled settlement ledger).
