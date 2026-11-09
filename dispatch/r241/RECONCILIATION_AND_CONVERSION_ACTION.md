# R241 — Canonical source identity and revenue readiness incident

**State: HOLD_UNSENT.** Source master is draft PR #175 at exact commit `d57ccdba3aee8f065e143e101c2945f4f3d01647`; prior readiness PR #201 and alternative manuscripts are NOT adopted. This branch adds evidence-only source reconciliation, no campaign manuscript edits. Child review PR will target branch `feature/dispatch-mind-campaign-pilot-20261030` without touching frozen homepage #49.

## P0 finding: downstream R235 manifest is NOT the master edition

Read-only GitHub retrieval of exact master six issue files and downstream `dispatch/r235/contract.json` (PR #1763, `091fa36106afc9d9aa2aa13ed3d522ff3ecec2e7`) shows **6/6 source SHA differences**, **4/6 preheader differences** (01,02,04,05), **1/6 subject differences** (Issue04 "Fourteen" versus downstream "Seventeen"), and **1/6 editorial CTA difference** (Issue01 Puységur archive versus `/the-missing-caption/`). The source references may correspond to separate drafts but **cannot be represented as exact canonical #175 bytes** absent a documented editorial adoption and per-edition provenance. This finding does not allege that the alternate content is incorrect; it blocks silently binding it to the master. The previous R237 historical Apollo correction still awaits founder adoption.

Canonical source file hashes and observed downstream values are in `SOURCE_RECORD.json`, which contains no subscriber PII, email addresses, tokens, or earning links. The original 6/6 Python campaign tests were executed natively from the earlier eight authenticated #175 source files at 2026-11-09 13:41 PT; they check basic structure and merchant holds, NOT source identity between PRs. New R241 gate tests source binding rather than pretending the native master suite covers this drift.

## Immediate safe repair (not implemented)

1. **Dispatch editor:** designate a single canonical authoring revision for each issue; only the founder may approve replacing original PR #175 copy. Preserve proposed alternatives on their isolated review PRs; do not merge or bulk rewrite.
2. **Claude, production engineering:** before any Jetpack post is created, produce a review-only manifest with GitHub issue blob SHA, exact subject, preheader, chosen CTA, offer classification, as-reviewed PDF/HTML digest, and separately approved status. Bind the actual WordPress preview back to that exact source, not a differently worded child contract.
3. **Site QA:** once separately authorized to create an unpublished WordPress draft, inspect actual native email-preview output, legal sender/footer, unsubscribe and preheader. Offline specimens cannot prove final Jetpack rendering. Never send a test email without explicit approval.
4. **Mind #171:** Zen12 Premium exact merchant page https://zen12.com/hnp advertises twelve levels and 48 recordings; its "one hour in twelve minutes" language remains a seller claim. Total Focus exact offer https://hypnosislive.com/mental-skills/total-focus says 33-minute / 47 MB; seller claims of perfect concentration are not independently proven. Refund FAQ https://hypnosislive.com/faq describes a fourteen-day window, limited to five sessions refunded per year. FV-named acceptance, EMAIL promotional permission, issued tracking URL, final cart and a live approved warmup guide are ALL UNKNOWN; do not turn on Issue03/05.
5. **Focus #129 / Claude:** verified current setting is ONE Jetpack list with full content, auto-send OFF and Fieldbook welcome configured. Provider counters total3/confirmed3/unconfirmed2 remain nonadditive; eligibility, confirmation-to-welcome delivery and PDF receipt are unknown. Confirmed signup must be grounded in authoritative provider state change, never button taps, `?subscribe=` or page text, and should be deduplicated with an opaque site-scoped key (no PII in Git).
6. **Commerce/Praxxis #820:** clicks, signup states, email opens and checkout intentions never count as paid sales. Use only settled merchant order data minus refunds/fees with a verified qualified-human session denominator for 7/30-day net revenue / 1k. Currently NOT_COMPUTABLE.

### Release matrix

| OFFER → STEP | BLOCKER | SAFE CHANGE/EXPERIMENT | EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Zen12 Premium → accepted offer | Named merchant, email permission and approved guide missing | Read account-issued partner terms / source approval; separately confirm guide publication | HARD_HOLD | Mind |
| Total Focus → high-intent guide | Seller claims vs proof and merchant rights | Preserve optional Issue05, no earning link | HARD_HOLD | Mind |
| Any edition → Jetpack post/preview | R235 source contract drifts from #175 | Pin master Git blob, explicit alternative adoption before preview | FAIL binding (6/6 hashes) | Dispatch + Claude |
| Focus → confirmed subscriber | Eligible audience and welcome not verified | Provider-confirmed one-event consent test, dedupe, no new list | UNKNOWN | Claude + Dispatch |
| Delivered email → legal opt-out | Actual mailing footer/MIME and unsubscribe unverified | Separately approved native preview and received-MIME analysis | UNKNOWN | Dispatch + Site QA |
| Buyer → realized margin | No settled order attribution or qualified-human denominator | 7/30-day verified reconciled net revenue only | NOT_COMPUTABLE | Commerce + Praxxis |

## Current read-only evidence

- Authenticated Jetpack status at **2026-11-09 21:40 UTC**: total=3, confirmed=3, unconfirmed=2, suppressed=0, current five posts `never_sent_opted_out`, no recipient totals. Newsletter `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=full`, welcome 52-page Fieldbook configured. This is NOT receipt or eligibility evidence.
- Live WP pages: /dispatch/ page 523, /focus/ page 1579, /editorial-standards/ page 17. No WordPress writes.
- Official native delivery: https://jetpack.com/support/newsletter/ (last updated Nov 4, 2026). FTC commercial email: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business.
- Source issues: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174 ; https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171 ; https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129 ; https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820.

**No emails, test messages, live posting, purchases, affiliate activation, new platform, tracking pixels, subscriber imports, or settings edits.** No production release authority is created by passing code tests.
