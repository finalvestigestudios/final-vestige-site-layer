# Dispatch R253 — Focus gift UI does not equal confirmed subscription
**Status: SOURCE-VERIFIED / OFFLINE-BROWSER-TESTED / LIVE-BROWSER-NOT-TESTED / CAMPAIGN HOLD_UNSENT.** 2026-11-10 UTC.

## High-priority finding
Authenticated read-only WordPress page 1579 (/focus/, last modified 2026-11-05T17:44:02) includes an inline script `fvf-gift-v2` that unhides `#fvf-gift` when the first `subscribe` URL parameter is truthy and **not** one of five negative strings. A `subscribe=pending`, `subscribe=unconfirmed`, `subscribe=1`, or arbitrary text is sufficient for the **client-side display**. Separately, a CSS class `is-subscriber` can unhide it on initialization or mutation. The hidden block displays the existing public PDF link and asks visitors to confirm their email. This is **not** proof of any newsletter submission or an actual unauthorized signup; the PDF was already publicly linked in the configured welcome. It is a **consent/measurement ambiguity**: visibility must never be counted as `confirmed_signup`.

The published page also carries `data-fv-event=focus_signup_click` on scrolling links and `focus_pdf_click` on the download. Neither is a confirmed subscriber or a paid customer. No final email-eligibility total has been obtained. The latest Jetpack status on 2026-11-10T09:31:43Z reports total=3, confirmed=3, unconfirmed=2; these are nonadditive and cannot establish email-eligible recipients.

## Exact-code verification
- `gift_signal_gate.mjs` and its `test_gift_signal_gate.mjs` are newly authored, no network or data writes. Native Node `node --test test_gift_signal_gate.mjs`: **26/26 PASS**, with exact locally executed and GitHub blob IDs recorded in evidence.json.
- The existing inline script was transcribed from authenticated WordPress editor response and executed in **offline native Chromium** fixtures: 15 URL cases (7 hidden, 8 displayed), initial class and mutation displays, provider-required transition tests. Six Python unittest methods PASS; **not a live site interaction**. The same scripts + tests are bundled in the local evidence ZIP; no customer data used.
- R252 route inspector was not rewritten; this is a separate subscriber-state boundary on top of R252 #1870, not a claim that subscription forms are broken.
- WordPress screenshot service returned site captures for 390px /focus/ and /dispatch/, but screenshots and REST extractions cannot establish real submission, received welcome, preheader, physical address, or unsubscribe.

## Release decision
All original six editions on master draft PR #175 remain unchanged: 4 editorial / 2 commercial. Original #201 QA, frozen homepage #49 and live site unchanged. No emails, test sends, WordPress writes, list operations, affiliate URLs, scheduled campaigns, account costs or analytics scripts. Issue 03/05 continue HOLD_MERCHANT.

## Highest-impact actions (OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER)
1. **Free Focus Fieldbook → source-tagged visit → gift reveal masquerading as signup** → distinguish `gift_ui_shown`/`focus_pdf_click` from a genuinely provider-confirmed and deduplicated `confirmed_signup`; only the latter counts as a lead. Source script + offline Chromium PASS, production tracking NOT VERIFIED. **Claude/Focus #129**.
2. **Fieldbook → email-eligible subscriber → counts disagree** → private *aggregate* filter `Email subscription: Subscribed`; do not export identities or sum 3+2. Read-only dashboard reports 3/3/2; eligibility UNKNOWN. **Focus/WordPress owner**.
3. **Welcome PDF → inbox/retention → final received delivery, unsubscribe and postal footer missing** → request separately approved safe native preview; received mail verification requires independent founder consent. **Dispatch/Site QA**.
4. **Zen12 optional offer → vetted warm-up guide → named partner EMAIL approval, exact earning URL and checkout/refund terms missing** → merchant-first evidence, no URL activation or benefit promises. Seller pages show competing promotional framing. **Mind Studio #171**.
5. **Paid order → realized net revenue → independent order/commission/refund/fee evidence absent** → reconcile provider settlements by 7/30-day cohort, not clicks. **Commerce/Praxxis #820**.

## Sources
- Live WordPress source: https://finalvestige.com/focus/ (page 1579), https://finalvestige.com/dispatch/ (page 523), https://finalvestige.com/editorial-standards/
- Official subscriber status definitions: https://wordpress.com/support/subscribers/ (reviewed 2026-11-04).
- Official subscribe-block modes: https://wordpress.com/support/wordpress-editor/blocks/subscribe-block/ (reviewed 2026-10-05).
- Welcome & confirmation: https://wordpress.com/support/newsletter-settings/
- Official sales pages, **seller claims only**: https://zen12.com/hnp and https://zen12.com/secret/
- FTC commercial email: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Original draft PR #175 and Issue #174; companion Mind Issue #171; Focus #129; conversion #820. Keep all production, sales and release gates **HOLD**.
