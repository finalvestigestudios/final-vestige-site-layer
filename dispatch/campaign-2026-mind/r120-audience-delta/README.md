# Dispatch R120 — subscriber-count drift and independent conversion evidence

**2026-11-04 19:33 UTC • DRAFT / UNSENT • Source of truth: Issue #174.**
Stacked on [R119 PR #975](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/975). Master originals [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) and prior preflight [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) are not edited. Homepage PR #49 remains frozen. This is not an alternate email platform, subscriber importer, sending job, or WordPress integration.

## A new production finding — not another newsletter draft

At 18:33 UTC, Issue #174 R119 documented total=2, confirmed=2, unconfirmed=2. At **19:32:58 UTC** and independently **19:33:44 UTC**, the connected WordPress Newsletter status showed **total=3, confirmed=3, unconfirmed=2, suppressed=0, paid=0, imported_last_24h=1**. Connected follower reporting showed **email=0; WordPress.com=3; total=3** (not additive with the newsletter tally). The settings remained newsletter ON, new-post auto-send OFF, excerpt delivery, no-reply, Final Vestige sender, configured 52-page Fieldbook welcome. The five most recent post notifications all remained `never_sent_opted_out`. Do **not** infer that the increase is an independently verified email signup, that the import counter caused it, that three addresses are email-reachable, or that any welcome was received. No subscriber email addresses were opened, exported, or stored.

This is a **change in aggregate counters**, with a concurrent import indicator requiring private provenance review. Confirmed-count growth is not the same as an authenticated native opt-in event. `imported_last_24h=1` is a vendor metric, not proof that an import was authorized or that it was a paid lead; do not accuse anyone of importing without evidence.

The prior 18:33 baseline is minute-precision evidence from Issue #174, not an independently saved exact-second raw response. The fixture's `18:33:00` is only a deterministic test timestamp. New snapshots use actual connector `as_of` values.

## Operational handoff — one blocking diagnostic first

1. **Dispatch / Claude (read-only):** Inspect WordPress's native subscriber overview/status filters privately, with authorized account access. Record aggregate by actual `Email Subscription` status and verified subscription source, and a redacted/opaque evidence reference to the latest change. Distinguish existing verified WordPress.com followers, pending confirmation and imports. Do not export or post names, addresses, IPs or identity metadata in GitHub. Identify why the import counter changed, *if that is observable*. Unknown is an acceptable result.
2. **Dispatch QA:** Verify the already configured welcome content without a new signup or email: current setting and real Fieldbook media record are configuration proof only. A real previously received welcome may be privately inspected if authorized; the earlier October 25 `Confirm your subscription` email is not welcome delivery. No test email or signup is allowed by this PR.
3. **Founder / Dispatch QA:** Validate a real rendered commercial Jetpack sample only after separately authorizing a safe preview/test. Confirm a **Final Vestige** physical postal address and an actual working unsubscribe mechanism; Automattic's footer address in a confirmation message does not qualify. Until then, cannot send.
4. **Mind Studio (Issue #171):** Obtain *named Final Vestige acceptance* with current permitted email promotion, actual link format/creative, privacy restrictions, final pricing/refund at checkout, and a live, independently vetted first-party buyer guide. Zen12 is a **single provisional** paid candidate; Hypnosis Live in Issue 05 is unapproved and remains reserved. Official seller pages are product marketing statements, not efficacy validation.
5. **Claude / Praxxis (Issue #820):** Only after native consent evidence, implement one `confirmed_signup` from authenticated WordPress transition; deduplicate via a private secret-keyed HMAC (never unhashed email or unhashed address). Pass `utm_source`, `utm_campaign`, `utm_content=Grok asset_id` only where a first-party landing visit can be legitimately associated; otherwise mark unattributed. A `campaign_landing` event, follower, click, PDF access or import does not establish a paid sale. Verify merchant-settled paid orders and refunds/fees independently; only then compute 7/30-day net revenue per 1,000 *qualified human* sessions. No extra tracking script.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE / EXPERIMENT → PASS/FAIL → OWNER

| Offer / step | Blocker | Change / experiment | Pass/fail evidence | Owner |
| --- | --- | --- | --- | --- |
| Fieldbook → confirmed subscriber | +1 confirmed counter, origin unknown; importer metric 1 | Private native subscriber-source review | PASS only with real consent event and distinct email eligibility; **UNKNOWN** | Dispatch / Claude |
| Fieldbook welcome → useful resource | Settings configured, inbox and PDF download unverified | Authorized existing received-message inspection, PDF GET & document verification | **UNKNOWN**; Oct 25 confirmation is insufficient | Dispatch QA |
| Editorial 01/02/04/06 → deep-dive | Excerpt transport and recipient footer unverified | Native editor preview / compliant inbox sample after founder permission | **HOLD** | Dispatch / Site QA |
| Zen12 / Issue 03 → buyer guide → order | Named merchant email rights + live vetted guide absent | Mind Studio verifies partner and one offer | **HOLD_MERCHANT** | Mind Studio |
| Hypnosis Live / Issue 05 → guide | Not accepted as cleared second offer | Preserve reserved 4:2 split; no live link | **HOLD_MERCHANT** | Mind Studio |
| Grok → Focus → order → net revenue | No reliably attributable sales/qualified denominator | Existing authorized analytics + independent settlement feed | **NOT_COMPUTABLE**, not $0 | Claude / Praxxis |

## Reproducible, read-only source checks

`python -m unittest discover -s dispatch/campaign-2026-mind/r120-audience-delta/tests -v`

The 27 *native Python 3.13* tests cover counts changing from 2→3, non-additive status semantics, invalid counters/time ordering, opt-in evidence, duplicates, WordPress already-verified pathway, PII rejection, fake click/settlement, refund deductions and missing denominators. Tests use SYNTHETIC tokens and financial amounts; `good` sample is **not** an actual subscriber. Verification of exact committed file blob hashes is required before declaring parity with local tests.

## Source discipline and release

- Official merchant pages: https://zen12.com/hnp and https://hypnosislive.com/mental-skills/total-focus ; descriptions and claimed results are seller claims only. Current displayed prices are **not** validated final purchases.
- Official FTC email obligations: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business and material connection disclosure https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking .
- Relevant policy: https://inspire3.com/privacy/ (potential identifying purchaser-information sharing, privacy check remains mandatory).
- Published pages: https://finalvestige.com/dispatch/ and https://finalvestige.com/focus/ ; Editorial Standards https://finalvestige.com/editorial-standards/ .
- No new list, email platform, spending, publisher address invention, social posting, WordPress write, email/test send, affiliate activation or dataset with personal addresses.
- Founder approval required for any final campaign creative/audience/timing and all live delivery.
- **ALL SIX: HOLD_UNSENT. Commercial Issues 03/05: additional HOLD_MERCHANT.**
