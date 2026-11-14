# R365 conversion-first release & measurement contract

**Primary outcome:** realized net revenue per 1,000 qualified human sessions, **not computable** until unique qualified traffic and independently settled, refund-adjusted orders exist. The subscriber flow is a prerequisite, not a proxy sale.

| Offer → step | Blocker | Offline change / experiment | Pass or fail evidence | Owner |
|---|---|---|---|---|
| Focus Fieldbook → confirmed signup | Total 3 / confirmed 3 / unconfirmed 2 overlap; 3 WordPress.com vs 0 direct-email labels do not establish eligible inbox count | Deduplicate by opaque provider confirmation ID; record one event `confirmed_signup` only for provider-confirmed, consent-scoped subscriber | FAIL UNKNOWN: no authoritative eligible-recipient export, never expose email addresses | Claude/Focus |
| Confirmed signup → received welcome | Welcome configured, not proven delivered | Validate authorized inbox artifact and working 52-page download with owner's consent, no subscription test in this sprint | FAIL UNKNOWN: config ≠ received | Founder/Focus |
| Issue 02 → Puységur article | Previous draft combined editorial claims and a duplicate CTA with Issue 01 | Source-qualified optional manuscript; single archive CTA and comparison exercise | PASS offline manuscript QA only; no user outcome demonstrated | Dispatch |
| Zen12 → vetted guide → paid order | Named EMAIL permission, affiliate link and live approved guide unavailable | No sending. Require merchant account authorization, Guide owner and checkout provenance | FAIL HOLD_MERCHANT | Mind/Commerce |
| Total Focus → vetted guide → paid order | Official page price drift and unverified partner permissions | Keep price absent from newsletter, resolve SKU / referred checkout / refund limits | FAIL HOLD_MERCHANT | Mind/Commerce |
| Dispatch → inbox opt-out | Actual postal, recipient and native rendering unknown | Non-sending native Jetpack preview in owner-authorized unpublished post; later owner-authorized received-message/opt-out test | FAIL HOLD_UNSENT | Founder/Dispatch |
| Grok → settled purchase | No verified asset IDs paired with actual order settlements | Preserve `utm_medium=organic_social` for creator; use `utm_medium=email` only on a future approved, actually sent Dispatch link, `utm_campaign=dispatch_pilot_2026_issue_02` and `utm_content=primary_archive`; no tracking script installed | FAIL UNKNOWN: no sourced human sessions or paid reconciliations | Grok/Praxxis/Claude/Commerce |

### Draft analytics event semantics (not deployed)
- `confirmed_signup`: fire **once** per hashed/opaque provider-supplied confirmation, after proof of completed consent, never when someone merely presses Subscribe or opens a PDF. Without a canonical provider ID, mark as unverified and do not emit. Minimize stored personal data; do not put an email or recipient ID in a URL.
- `email_cta_click`: name an approved issue_id and CTA destination only after a genuine email send; never declare an email click from an offline preview.
- `paid_conversion`: **only** import independently confirmed settled sale or commission receipt (with rights to access it); subtract refunds and platform fees to derive realized net revenue. Do not compute fake tiny-list experiments, open rates or customer outcomes.
- 7-day / 30-day cohorts by original qualified source campaign, and all unknown matches explicitly unassigned rather than inferred.

### Disposition
All six originals HOLD_UNSENT; 03/05 additionally HOLD_MERCHANT; optional Issue 02 NOT_ADOPTED. Existing new-post auto-send OFF remains untouched. No extra list, provider, attribution pixel, creator posting, tests by email, WordPress writes or spend.
