# R273 independent buyer-fit and consent evidence — 2026-11-10 PT
**HOLD_UNSENT** for every original issue; **HOLD_MERCHANT** for Issues 03 and 05; new Issue 05 is **NOT_ADOPTED**. Stacked on draft PR #1997; source-only.

## New provider-confirmation nuance
WordPress documentation says an address already verified with WordPress.com **may not need a new confirmation email click**. The analytic contract MUST therefore treat a first authenticated Jetpack transition to Email subscription=Subscribed (with provider consent provenance) as the confirmed_signup source of truth, not a mandatory observed click. Deduplicate by opaque provider identity/event transition and never count a repeat attempt/reactivation as a new person. Separate Reader-only, Not confirmed, Bounced, Emails paused, Not sending, and Unsubscribed states. Do not infer consent from Focus ?subscribe= query values, public Fieldbook display, WordPress.com follower totals, Zen12 email enrollment, or marketing messages. Do not export identifiers.

Read-only WordPress status 2026-11-11 05:32 UTC: newsletter enabled; new-post auto-send OFF; email format FULL; welcome configured to deliver same registered Fieldbook; total 3, confirmed counter 3, unconfirmed requests 2; follower email 0/WP.com 3; latest posts never_sent_opted_out. Counts are NOT additive. Actually currently eligible: **UNKNOWN**. Welcome inbox receipt, public PDF binary, genuine received unsubscribe and publisher physical address: **UNKNOWN**.

## Specific commercial-claim audit
- Total Focus official seller page lists 33-minute, 47-MB download, with bold claims of brain reprogramming and perfect focus. Format is seller-reported; claimed improvement is NOT independently proven for this MP3.
- Hypnosis Live official FAQ describes instant MP3 access, 14-day refunds limited to **five sessions per year**; note qualification even if seller headline says 'no questions asked.' Do not carry a current displayed price into an unspecified affiliate checkout.
- NCCIH reviews hypnosis evidence for certain conditions, not this product's focus claims. 2024 hypnosis-theory review does NOT validate branded audio effectiveness.
- A general affiliate-program page and prior merchant marketing mail do NOT establish Final Vestige partner approval, issued earning URL, allowed email channel, or sales proof. Mind & Affiliate #171 owns the canonical live buyer guide and permission evidence. NONE VERIFIED.

## Compliance and attribution
The commercial disclosure is immediately beside the one INACTIVE buyer-guide CTA. Other references are research citations, not purchase CTAs. FTC requires truthful header/subject, clear identification, sender-specific valid physical postal address and compliant opt-out as applicable to the message's primary purpose. Opt-out need not technically be one-click: FTC guidance allows a reply or one-page mechanism, honor requests within 10 business days, keep mechanism available >=30 days. The static HTML/plaintext is not a real Jetpack email. Do not initiate an unauthorized test send or import.
Proposed (not deployed) eventual email attribution: utm_source=dispatch, utm_medium=email, utm_campaign=dispatch_mind_2026_pilot, utm_content=issue05. Source-tagged visit/click is not a paid order. One first-party confirmed_signup when authenticated Jetpack confirms new subscription; 7/30d cohorts; revenue only from independently reported settled commissions net refunds/fees, tied to qualified human sessions. No new script or platform. Net/1000=NOT_COMPUTABLE.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE → PASS/FAIL → OWNER
| Offer | Step | Blocker | Change | Proof | Owner |
|---|---|---|---|---|---|
| Total Focus | Dispatch 05 → buyer guide | No partner email approval, earning link, verified live guide | Confirm exact route, terms, permissions and approve ONE guide | HOLD | Mind #171 |
| Focus Fieldbook | signup → delivered welcome | Unknown provider-eligible population/received welcome/PDF | Obtain aggregate 'Email subscription=Subscribed' status and authorized recipient-owned proof | UNKNOWN | Claude/Focus #129 |
| Dispatch | received email | Publisher-specific postal and unsubscribe unverified | Approval-gated real Jetpack preview and opt-out QA; no subscriber send | HOLD | Dispatch #174 |
| Grok → Focus | qualified social source | Asset-to-first-party confirmation join absent | Existing TASK-008 immutable asset_id/UTMs; no social queue changes | NOT VERIFIED | Grok/Praxxis |
| Purchase | net settled revenue | No authenticated checkout/refund/fee evidence | Source-of-truth private merchant reconciliation | NOT COMPUTABLE | Commerce/#820 |

Sources:
- Merchant's official Total Focus offer and feature claims: https://hypnosislive.com/mental-skills/total-focus
- Merchant's official FAQ and refund annual cap: https://hypnosislive.com/faq
- NIH NCCIH evidence on hypnosis, not the seller's MP3: https://www.nccih.nih.gov/health/hypnosis
- 2024 review of hypnosis theories, not product efficacy: https://pubmed.ncbi.nlm.nih.gov/39032268/
- Final Vestige historical Puységur source archive: https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/
- FTC health product evidence standard: https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- FTC CAN-SPAM compliance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- WordPress exact email subscription states: https://wordpress.com/support/subscribers/
- WordPress preverified-account confirmation exception: https://wordpress.com/support/newsletter/subscribe-to-a-newsletter/
No emails, tests sent, posts, subscribers, WordPress settings, affiliate activation, social posts, scripts, merges or expenses.