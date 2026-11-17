# Dispatch R422 — OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER

**Release:** ALL SIX `HOLD_UNSENT`; commercial slots 03/05 `HOLD_MERCHANT`; original 04 `HOLD_COPY`; candidate copy unadopted. No paid offers activated, no email/test email/list operations, no WordPress writes, no new expense. The six-issue draft remains 4 editorial + 2 commercial. Master #175; QA baseline #201; previous stack #2858; this change is additive only.

## 1. Merchant-origin claim drift: source pages are not partner permission

Read again 2026-11-17 using **specific seller-owned pages**:

**Zen12 / candidate commercial Issue 03.**
- https://zen12.com/about describes 12-minute audio sessions, twelve levels, four session styles (music, guided, white noise and nature). It claims the benefit of one hour in twelve minutes and automatic effects. These are **seller assertions**, not independent evidence of product-specific attention, physiological, mental-health or wealth outcomes.
- https://zen12.com/secret/ advertises a distinct coupon/promotion funnel, showing $37 with a named code compared against $87. This is not evidence of Final Vestige earning credit or of the customer's eventual live checkout and returns. The general https://zen12.com/ page shows other packages/prices; never quote one as universally current.
- **Must collect from Mind/Commerce:** Final Vestige account acceptance in the seller's actual partner system, permission for channel=EMAIL (not just web/social), exact approved Zen12 SKU/bundle and creative, actual issued earning URL, allowed region/terms, founder-approved LIVE first-party warm-up guide, final referred checkout and return policy. All presently **NOT VERIFIED**.

**Hypnosis Live Total Focus / commercial Issue 05.**
- https://hypnosislive.com/mental-skills/total-focus describes a **33-minute / 47-MB** recording, a current individual and bundle surface, plus dramatic concentration promises. Product metadata and marketing claims must not be conflated.
- https://hypnosislive.com/faq describes a **14-day** refund request window while limiting refunds to **five sessions per year**, with further processing timelines. A general satisfaction guarantee without that qualification is incomplete. The exact referred checkout could vary. Hypnosis efficacy studies do not validate this named commercial recording.
- **Must collect independently:** named Final Vestige publisher EMAIL rights, exact single-item vs bundle referral, approved creative, active earning URL, guide, checkout and returns, settlement reporting. None is established. Do not transfer a Zen12 grant to Hypnosis Live.

**Commission disclosure near qualifying offer (draft only, not a live placement):** “If you buy through an approved link in our review, Final Vestige Studios may earn a commission. Our historical findings and evaluation are independent of that relationship.” Place beside the *one approved guide CTA*, not merely in a distant footer; do not claim an agreement exists before verified.

## 2. Compliant inbox

FTC official https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business explains the commercial-primary-purpose rule, truthful sender/subject, valid postal address, reasonable unsubscribe and timely opt-out. A purely editorial subject does **not** automatically exempt a message whose primary purpose is promotion. A WordPress or Automattic return address printed in a subscription confirmation is **not** proof of a valid **Final Vestige Studios** mailing address in an actual commercial Dispatch issue. The seller's London address is likewise not Final Vestige's publisher address.

**Evidence to pass:** capture native Jetpack preview on actual draft (NO send), inspect sender identity and unsub/postal template, verify the publisher address, and obtain explicit legal review. Do not put address placeholders into live messages. No founder-authorized received-email or unsubscribe test exists yet.

## 3. Source-attributed conversion acceptance

| Offer → step | Current blocker | Change or experiment *after authorization* | Pass/fail evidence | Owner |
|---|---|---|---|---|
| Free Fieldbook → confirmed lead | Gift exposed by client URL/class; dashboard totals ambiguous | Use one authenticated, deduped provider event after consent; no browser success proxy | Provider eligibility/welcome witness; today HOLD | Focus + Claude |
| Zen12 → first-party guide → paid sale | No named EMAIL permission, LIVE vetted guide or issued earning link | One honest buyer-guide CTA in commercial Issue 03, **only after** approval | Merchant partner authorization and independently settled referred order; today HOLD | Mind + Commerce + Founder |
| Total Focus → first-party guide → paid sale | Same rights and bundle/returns mismatch | Independently approve the second reserved slot, do not piggyback Zen12 | Exact SKU, checkout, return policy, settlement; today HOLD | Mind + Commerce |
| Dispatch → reader inbox | Native preview, address, opt-out not witnessed | Actual non-sending editor preview + separately authorized inbox/opt-out verification | Received output with lawful publisher identity/links; today HOLD | Founder + Dispatch |
| Grok asset → qualified traffic | No actual human-session and paid-order crosswalk | Verify real asset_id and existing Claude source tagging; no duplicate measurement | Real 7/30-day cohorts with independent paid settlements; today UNKNOWN | Grok + Praxxis + Claude |

Attribution conventions align to TASK-008 in the current shared Drive: original `utm_content` is Grok's unique real asset ID. A prospective email click uses `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue_03` only if Claude's existing pipeline can preserve first-touch/consent without manufacturing a sale. Do not put PII in UTMs. No server-side commerce instrumentation belongs to Dispatch.

Commercial formulas, **not currently measurable**:
- `realized_net = verified_settled_gross - refunds - fees - reversals` (source and timestamp required)
- `net_per_1000_qualified_sessions = 1000 * realized_net / audited_qualified_human_sessions`; if denominator is missing or 0, report **NOT COMPUTABLE**, never zero by default
- `lead_to_customer = distinct paid customers with verified lead linkage / distinct provider-confirmed leads` when consented linkage exists. With three dashboard subscribers, do not report fake A/B results, uplift or percentages without tiny-n warning.

## 4. What this sprint actually proved

- **Live, read-only WordPress (2026-11-17 11:36 UTC):** newsletter ON, post auto-send OFF, full/no-reply, total3 confirmed3 unconfirmed2, separate Stats WP Reader3/email0. Not an eligible recipient count.
- **Focus client logic (same run):** a nonblocked `subscribe` query parameter **or** an `is-subscriber` CSS class can expose the free PDF download. This is **not** a provider-confirmed signup.
- **Connected Gmail scoped search:** zero matches for the current Fieldbook welcome phrase/title after 2026-10-28 in the searched mailbox; not a universal deliverability conclusion.
- **Master #175:** all eight unchanged source/test Git blobs were independently compared to an earlier byte-for-byte package, then native Python 3.13.5 **6/6 PASS**.
- **R422:** new exact-byte Git blob checked synthetic JavaScript gate/test module, executed natively in Node v22.16.0 **25/25 PASS**; no production hookup.
- **Not witnessed:** native email Preview/MIME, registered mailing address and unsub, partner approval, guide checkout, actual welcome receipt, confirmed unique recipient, qualifying paid settlement or audited human-session denominator.

**Decision:** Do NOT send or schedule any of the six. Homepage flagship remains priority one; frozen PR #49 and Claude's website production code are untouched. All affiliate and editorial draft alternatives require separate founder adoption.
