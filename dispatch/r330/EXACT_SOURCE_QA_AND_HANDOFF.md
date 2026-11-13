# Dispatch R330 — exact-source QA, evidence authority and non-sending decision

**Date:** 2026-11-13 (Pacific). **Focus:** transfer gap between canonical offline HTML and actual native Jetpack POST-backed email, not another competing manuscript. **Release state:** ALL SIX HOLD_UNSENT; Issues 03 and 05 additionally HOLD_MERCHANT. None of the optional R321–R327 alternate issues have been adopted.

## Source, branch and no-conflict inspection

- Read latest [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) (including newest R329/Mind handoffs), companion [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) and conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).
- Re-read original master [draft #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at exact unchanged head `d57ccdba3aee8f065e143e101c2945f4f3d01647`; read previous [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), canonical preview [#2337](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2337) and immediate stacked [#2343](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2343) at head `8d6f7531d04f85f1995e7805c29343d273ca1a97`. The R330 branch was created from precisely that R329 head.
- Inspected authenticated public-facing WordPress /dispatch/ #523, /focus/ #1579 and /editorial-standards/ #17 in read-only `context=edit`; site content, form/welcome and standards preserved.
- Read actual live `wpcom_jetpack_newsletter` status at **2026-11-13 13:34:27 UTC** and get_settings. Enabled/can-send true; auto-send OFF; full format; reply no-reply; configured Fieldbook welcome; total=3,confirmed=3,unconfirmed=2 overlap; actual deliverable audience unknown. Five recent posts were marked never_sent_opted_out, without claiming a lifetime history.
- Read Google Drive original Grok/Praxxis TASK-008 under its actual connected document; no change to social queue or attribution system.
- Independently checked [WordPress post/email behavior](https://wordpress.com/support/newsletter/send-newsletter-emails/), [native preview and full/excerpt](https://wordpress.com/support/newsletter/email-appearance/), [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [Zen12 seller](https://zen12.com/), [Zen12 free-gift dual consent](https://zen12.com/gift), [Total Focus SKU](https://hypnosislive.com/mental-skills/total-focus), and [Inspire3 public affiliate portal](https://affiliates.inspire3.com/).
- Targeted private Gmail search read three consumer/promotional messages dated Nov 10–11, but **no Final Vestige-specific merchant email permission**. Promotional copy claiming Tesla biorhythms was NOT treated as source evidence or allowable affiliate creative. No private mailbox content, email addresses or tokenized URLs included here.

## Exact-source executed QA: PASS, with scope limits

| Check | Result | What it does NOT prove |
| --- | --- | --- |
| Original unchanged PR #175 Python unit suite, archived source `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v` | **6/6 PASS**, native Python on current run | Site subscriber delivery, merchant rights or production renderer |
| Original four source Git blobs independently matched remote #175 | manifest `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`; tests `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`; 03 `aeeef34efea0cc281f69901488e4501fea851245`; 05 `a9dfaa450ba025a7b5113ade8a294d6dbad778dc` | All remote files were not refetched for native test from scratch; archived originals were blob-identical |
| R330 **exact GitHub-fetched** `post_transfer_guard.cjs` and tests executed in a V8 CommonJS-test shim | **27/27 PASS**, 0 failures | Not a native Node execution or production deployment |
| Remote GitHub readback | **5/5** added files before evidence report; all 4:2 and HOLD status assertions true | WordPress post was not created, rendered or mailed |
| Exact remote blob identities | guard `1a1c6426013ea41d254fce65d71106da2dca64f0`; test `550717e53b1f85b3a585bed879ae0ab137a6d4b3`; contract `92906dc7d417f75851c78af52d889db54263dc00` | Running source checks does not establish deliverability |
| Actual native WordPress preview or received-message QA | **NOT VERIFIED / NO TEST SEND** | No actual subject, preheader, footer or inbox appearance certified |

The guard checks the actual WordPress **transfer proposal**, not the mail server: correct title-as-subject, full text acknowledgement, explicit per-post email opt-out, absence of internal review wording and required tokens, no direct unexpected merchant links or hyperbolic seller claims, one relevant CTA, merchant permission and adjacent disclosure, plus external evidence for physical footer, inbox and consent. It always reports `HOLD_UNSENT`, including synthetically all-green inputs; a local passed test cannot authorize a send. It contains no API operations or tracking.

## Critical content and revenue interpretation

The six offline R328 preview files are valuable but cannot safely be pasted as a WordPress email: the site is FULL-format, title controls actual subject, and native client footer/preheader cannot be proved by static preview. This specific incompatibility is the R330 **new blocker/change**. It avoids shipping internal legal placeholders or ad-copy claims to a real subscriber.

There remains no reliable count of email-eligible recipients, completed welcome receipt, native unsub functionality, authenticated affiliate EMAIL channel terms, issued earning URL, live reviewed guide, verified price/refunds or independently settled merchant order. No proposed `confirmed_signup` or `paid_conversion` event has been deployed. Neither a browser query nor a merchant sign-up substitutes for Jetpack provider consent.

**Net revenue per 1,000 verified qualified-human sessions = NOT COMPUTABLE**, not $0, until real qualified-human denominator and settled commission net of returns/fees exist. For tiny counts, publish descriptive counts only, never statistical lift.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE → PASS/FAIL → OWNER

| Offer / funnel | Priority blocker | Concrete change / experiment | Evidence now | Owner |
| --- | --- | --- | --- | --- |
| Zen12 Premium → approved first-party guide → paid commission | No authenticated merchant EMAIL rights, issued earning link, checkout and LIVE approved presell | Mind/Commerce supply exact account terms, guide and checkout proof; Dispatch reviews direct-response claim language and adjacent disclosure | **FAIL: merchant rights NOT VERIFIED** | Mind #171 / Commerce |
| Dispatch editorial → legitimate inbox | Offline HTML not native post output; title/preheader/QA tokens could leak | Transfer guard on proposed post; founder-authorized native preview; separately approved genuine inbox test; witness valid FV publisher address and functional unsubscribe | **GUARD PASS as code; RECEIPT FAIL/UNKNOWN** | Dispatch #174 / Founder |
| Focus / Dispatch → confirmed eligible subscriber | Counters 3/3/2 overlap; no observed Welcome/Fieldbook delivery | Claude authenticates provider new site enrollment, email eligibility, opt-out and current welcome receipt read-only, with private dedupe | **UNKNOWN** | Claude / Focus #129 |
| Grok asset → qualified human session → owned guide | No confirmed authentic campaign asset/session join | Keep TASK-008 Grok ownership; use existing privacy-safe campaign UTM and Claude analytics only after permitted code review | **UNKNOWN** | Grok / Praxxis / Claude #820 |
| Actual order → realized cash | Neither attributed settled orders nor refund/fee records shown | Commerce-owned export with private deduplicated order IDs, reversals and 7/30-day cohorts | **NOT COMPUTABLE** | Commerce / #820 |

**Zero production changes:** no WordPress post/draft/preview/test mail or list action, no external send, no site setting, no published CTA, no new analytics instrumentation, no affiliate activation or spending. Frozen homepage PR #49 remains untouched. All changes in separate `dispatch/r330/` paths on a stacked draft branch.
