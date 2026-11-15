# Conversion-first owner handoff and evidence contract

**Business priority: independently settled net revenue, not messages, clicks or impressions.**

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT (draft only) | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Zen12 Premium → validated guide → actual purchase | No named email permission, issued earning link, approved live guide or referred checkout | Mind's unpublished text-only pre-sell vs optional video concept; do not adopt an A/B result | FAIL: official consumer pages only; PR #2553 unmerged; paid order proof absent | Mind / Commerce |
| Focus Fieldbook → confirmed subscriber | Total3/confirmed3/unconfirmed2 overlap and WP.com followers3 vs direct-email0 | Normalize unique provider-confirmed `confirmed_signup`; one logical event per provider-confirmed ID, no PII event payload | FAIL: current aggregates don't establish unique opted-in inboxes | Claude / Focus |
| Welcome → Fieldbook delivered → reader retained | No observed received welcome/guest PDF | Source-based verification, then authorized inbox validation; do not generate test sends without founder | FAIL: configured welcome & WP media item do not establish received message | Focus / Founder |
| Dispatch → compliant inbox | No native received preview, verified FV address, working unsubscribe | Safe read-only native Preview email of approved preexisting draft when enabled; opt-out test only on explicit approval | FAIL: static .eml and HTML are not native WordPress | Dispatch / Founder |
| Grok asset → purchase | No unique qualified sessions or merchant paid order joins | Use existing TASK-008 conventions, no duplicate analytics scripts | FAIL: no provider settlement ledger or qualified-session denominator | Grok / Praxxis / Claude / Commerce |

Attribution: `utm_source` platform slug; `utm_medium=organic_social` for Grok referral; `utm_campaign=<topic_cluster>_pilot_2026_11`; `utm_content=<immutable_asset_id>`. Email traffic, **after approval**, uses `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue_0N`, and does not overwrite first-touch Grok source. Avoid subscriber IDs in URLs. Confirmed lead only after provider confirmation, de-duplicate by provider-owned opaque key using privacy-safe aggregate. Distinguish eligible people, attempts, page visits, outbound affiliate clicks, settled orders and paid commissions. Revenue/1k qualified humans = 1,000 × (settled gross paid receipts minus refunds, platform/affiliate fees and direct transaction costs) / independently measured qualified-human sessions; do not display if denominator is 0/unknown. Use 7/30-day cohorts and suppress comparisons on tiny samples.

**Cross-team source-of-truth:** Dispatch #174 / Focus #129 / Mind #171 / conversion #820; Grok's TASK-008 Google Doc remains Grok/Praxxis owned. Homepage #150 / frozen #49 untouched.
