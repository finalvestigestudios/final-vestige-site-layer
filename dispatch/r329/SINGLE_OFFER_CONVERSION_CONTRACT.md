# R329 — a single-offer Dispatch subscriber-to-customer contract (NOT A SCHEDULE)

The founder's **original six weekly UNSENT drafts** remain 4 editorial / 2 commercial-review-pending: #01 perception → #02 historical testimony → #03 optional Zen12 review → #04 Apollo 1 → #05 optional Total Focus review → #06 evidence log. The optional manuscript revisions R321–R327 are **not adopted**; R328 already renders all six existing issues. This document describes a *conditional reader journey*, not a seventh email, an automated drip sequence, or authority to contact subscribers.

## Buyer journey first, messaging second
**Candidate paid offer:** Zen12 Premium ONLY as a **hypothesis**, not an approved or currently merchant-eligible offer. Do not substitute a different SKU or direct merchant link without Mind/Commerce signoff. Readers can reach the free source archive and the ultimate buyer guide without subscribing. No psychological pressure, scarcity or overclaims.

| Reader state | Legitimate reader value | Optional transition / legal gate | Outcome actually measurable |
| --- | --- | --- | --- |
| Grok's actual published history/perception asset | Fully sourced on-site explanation | `utm_source` platform; `utm_medium=organic_social`; unique `utm_content=asset_id`, scoped `utm_campaign` | Qualified-human first-party session only if bot filtering/source provenance corroborate it |
| Existing /focus/ landing and Fieldbook | Genuine useful 52-page workbook | Existing Jetpack Subscribe; explicit consent text; no second list | Signup ATTEMPT; not a confirmed lead |
| Authenticated provider confirmation OR immediate WordPress account enrollment | Welcome Fieldbook (when independently witnessed) | Provider-origin new site enrollment, email eligibility and consent; dedupe one unique subscriber | `confirmed_signup` only once on authentic new enrollment, never on display of gift or old follower record |
| Issue #01 or #02 historic evidence | Free historical/perception sources | One editorial CTA; preserve history-first expectation | Website editorial CTA click only, not a sale |
| Issue #03 buyer-checklist invitation | Free comparison checklist + no-purchase control exercise | **HOLD** until first-party guide is actually LIVE, earning permission is authorized and near-link disclosure is rendered | Guide click; no attribution of payment |
| Independent buyer guide + optional merchant checkout | Product format/terms, honest uncertainty and original source links | Clear permission/disclosure; seller's newsletter opt-in separately explained; merchant's approved earning link only | Affiliate outbound click; NEVER a purchase |
| Merchant independently reported paid order | Proof of customer purchase | Settlement/refund/fee reconciliation, stable non-PII external order key, approved source join | Paid customer; realized net receipts |

**Issue #05 stays commercial-review-pending** as the second of two reserved potential offer slots, but is *not* part of the ONE-offer initial conversion experiment. Its presence should not split a tiny cohort into false A/B groups. There is no basis for declaring either product the winner.

## Attribution convention — adapt existing measurement, no duplicate script
- Preserve Grok/Praxxis owned `asset_id` exactly; `utm_source` actual platform (e.g. `tiktok`, `youtube`), `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11` only if that is Grok's assigned campaign, and `utm_content=<asset_id>`. Do not fabricate published assets.
- For newsletter editorial CTA: propose `utm_source=dispatch`, `utm_medium=email`, `utm_campaign=dispatch_pilot_2026_11`, `utm_content=issue_03_zen12_review`, but add to real links **only if authorized** and tested with the existing measurement instrumentation. Do not append a merchant sub-id or duplicate instrumentation.
- `confirmed_signup` **must be sourced from the authenticated provider's actual new subscription event**, not from a redirect query, screenshot, popup, download, email entry or same-site visit. Two valid provider paths: email-link confirmation and immediate WordPress-account subscription. On reconfirmation or imported/existing subscriber, no new lead credit. Reconciliation must remain private; never expose raw subscriber identities.
- A newsletter link click proves intent only, not that a subscriber consented to the merchant's list. A vendor email opt-in is not a Dispatch opt-in.
- Join qualified human source session → (if applicable) verified new subscriber → approved guide click → independently reported settled merchant order. Attribution must be **explicitly declared and reproducible**; when a linking key is absent, report `unattributed`, not a guessed Grok sale.
- Unique sales: deduplicate merchant order IDs across updates; partial refunds and commission reversals reduce realized net, not gross customer order totals. Do not double count same subscriber across 7-day and 30-day views as independent users. Report small samples as counts, not statistically meaningful lift.
- `net_revenue_per_1k_qualified_human_sessions = 1000*(independently_settled_sales_revenue - refunds - fees - commission_reversals) / verified_qualified_human_sessions`. If numerator provenance or denominator is absent, return **NOT COMPUTABLE**, never zero as a stand-in.
- Data minimization: use opaque/rotated internal IDs with separate consented storage, no emails in the GitHub ledger or URLs, no household-level profiling or remarketing inference. Keep an evidence URL/timestamp and aggregate count, not per-subscriber content.

## Non-sending progression hypothesis
- **Phase E / editorial trust:** Issues #01–#02 earn reader attention by revealing one genuine difference between documented observation and interpretation. One link to a real free archive per issue, not an affiliate teaser every time.
- **Phase V / voluntary evaluation:** In draft Issue #03, make the 12-minute practical comparison the center; the *only* CTA becomes the first-party Zen12 buyer guide **if and only if** the route is live and independently approved. Offer a free alternative inside copy rather than an unrelated second prominent CTA.
- **Phase C / commercial measurement:** Reader who chooses to visit the guide can independently decide to follow a disclosed, permission-checked earning link. Conversion is reported ONLY when a settled commission is independently evidenced; otherwise no commercial success claim.
- **Phase R / relationship continuity:** Issues #04 and #06 return to historical investigations and useful critical-thinking practice. Issue #05 stays behind separate product-rights gates; no fallback auto-adoption or forced promotion.

## Preflight failure criteria
Any unknown provider email eligibility, final publisher postal address, functional unsubscribe, genuine inbox rendering, approved guide, earning link/channel permission, final offer terms, or final founder send approval remains **HOLD**. A product-specific FTC claim problem is an additional HOLD for #03/#05. `receipt_guard.cjs` reports `HOLD_UNSENT` in all cases by design.

## Owner and pass/fail board
| Offer → funnel | Concrete blocker | Next change / experiment (never live without approval) | Pass/fail evidence | Owner |
| --- | --- | --- | --- | --- |
| Zen12 Premium → eligible guide → paid purchase | Merchant account/email permission and approved guide absent | Private partner-term attestation + evaluate a single first-party presell | **FAIL / no approved earning link** | Mind / Commerce |
| Focus → confirmed lead | Overlapping counts; no provider event record or observed welcome receipt | Private provider-event join and non-sending test plan | **UNVERIFIED / 3 total, 3 confirmed, 2 unconfirmed; no eligible unique count** | Claude / Focus |
| Dispatch → genuine inbox | Publisher postal address, unsub function, raw received rendering unknown | After separate authorization, run private MIME/footer acceptance protocol | **FAIL / no received proof** | Dispatch / Founder |
| Grok → site qualified human | Published real asset IDs and verified human-session joins not supplied | Reconcile TASK-008 with existing tracking; avoid new scripts | **UNVERIFIED** | Grok / Praxxis / Claude |
| Paid sale → net revenue | No settled order/refund/fee proof or qualified-session denominator | Reconcile merchant settlements vs existing first-party measurement | **NOT COMPUTABLE** | Commerce |

References: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174 | https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820 | https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129 | https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit
