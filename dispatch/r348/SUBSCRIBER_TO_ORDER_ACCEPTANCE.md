# R348 — One subscriber-to-customer proof contract (NON-SENDING)

**Purpose:** An executable checklist for Claude/Focus + Dispatch + Commerce to accept **one** lead and **one** revenue outcome, without adding a tracking script, new list, third-party platform or any live change.

## Highest-intent path (hypothesis, not proven funnel)
Grok-created history/Mind asset → exact audience-aligned investigation or Focus field guide → **voluntary Jetpack signup** → provider-confirmed status and consent → existing Fieldbook welcome → one optional permission-cleared independent buyer guide → authenticated merchant-paid order / net commission.

No buyer guide is LIVE/APPROVED, so the commercial step is blocked. The Fieldbook's direct PDF can be downloaded without signing up; a download is **never** a `confirmed_signup`.

## Source-of-truth event agreement
| Stage | Event | Acceptance standard | Must NOT count as |
|---|---|---|---|
| Social acquisition | `qualified_human_session` | Claude-authoritative, consent-respecting session with genuine channel and immutable Grok asset ID in `utm_content`; bot filtering documented | Impressions, video views |
| Visit | `landing_view` | Onsite page + verified source-tagged session | Subscriber or paid sale |
| Interest | `cta_click` | First-party site CTA with event_id and actual target | Checkout, order |
| Signup attempt | `signup_attempt` | Local form transition; never carries raw email in analytics | Confirmation |
| Provider opt-in | **`confirmed_signup`** | Jetpack authoritative subscription confirmation with stable provider-event identifier, not aggregate counts; consent status and timestamp; no subscriber email in shared reporting | PDF download, follower, attempt |
| Welcome | `welcome_received` | Only an authorized real recipient inbox record, not configured welcome text | Delivered automatically |
| Paid outcome | `settled_order` or `settled_affiliate_commission` | Payment/merchant source-of-truth reference and settlement, deduped by order/refund ID; refunds/fees separately verified | Merchant visit or offer click |

**Deduplication:** Define `confirmed_signup` once by provider unique confirmed subscription identifier plus confirmation state transition; ignore repeated web-form submits and replayed browser events. Hold if provider exposes only aggregated 3/3/2 counts. Do not export, log, embed or display email addresses, IPs or raw subscriber IDs in GitHub evidence.

**Email source-tag convention** (proposed only, not live): `utm_source=dispatch&utm_medium=email&utm_campaign=pilot_mind_2026_11&utm_content=issue_04_editorial`; actual link mapping and preserving first-touch Grok origin must be reviewed by Claude. Do not overwrite original first-touch source with email last-touch. Avoid personally identifying URL parameters. Issue 03/05 tagging only AFTER merchant approval and active vetted first-party guide.

**Revenue acceptance:** `realized_net_revenue = settled_gross - refunds - fees` (for own goods); for affiliates `settled_net_commission - reversals - fees`, using merchant settlement reports only. Then `net_revenue_per_1000_qualified_sessions = 1000 * realized_net_revenue / qualified_human_sessions`. An absent authenticated denominator or financial input means **NOT COMPUTABLE**, never zero. 7- and 30-day source cohorts; flag microscopic samples; do not publish subscriber identities, A/B uplift or claims of commercial success.

## Actual source snapshot (authenticated WordPress read-only 2026-11-14 06:35 UTC)
- Newsletter enabled; new-post emails OFF; full content; reply-to no-reply; welcome text configured with 52-page PDF.
- Jetpack aggregates: total 3, confirmed 3, unconfirmed 2; **categories overlap**. WordPress.com vs direct-email follower counts are separate categories, not summable to eligible inboxes.
- Last five recent post records: `never_sent_opted_out`; no proof of a current campaign delivery.
- True deliverable recipient count, subscriber consent timestamps, confirmed/welcome receipt, publisher postal identity, working opt-out, native received rendering: **UNKNOWN**.

## Release gate owners
| Offer → stage | Blocker | Change / experiment | Pass evidence | Owner |
|---|---|---|---|---|
| Zen12 → approved guide → sale | Channel rights + link + unpublished page | Obtain and attest exact permission, make vetted guide live ONLY with founder approval | Signed terms, issued affiliate URL, reachable authorized guide | Mind/Commerce |
| Total Focus → guide → sale | Same; seller price currently displays promotional/list mismatch | Confirm merchant checkout, refund terms and email permissions without quoting provisional prices | Merchant-authorized current offer and checkout proof | Mind/Commerce |
| Focus → subscriber → welcome | Non-additive subscriber counts, PDF accessible without opt-in | Provider private status reconciliation + controlled approved inbox inspection | Documented deduped provider confirmation, actual received welcome | Claude/Focus/Founder |
| Dispatch → received email | No authorized test, valid FV postal or real unsubscribe proof | Verify native Preview email without sending; future founder-authorized controlled received-email test | Captured actual rendered footer, verified one-step opt-out in authorized test | Dispatch/Founder |
| Grok → qualified human → paid order | No linked actual asset/session/settlement facts | Link existing Grok asset ID and site sessions to authenticated transactions | Aggregate 7/30-day paid data, refund/fee records | Grok/Praxxis/Claude/Commerce |

**Status:** BUILT source-only; offline checks may PASS; no attribution instrumentation, Jetpack mail, merchant purchase or conversion is VERIFIED. This is not an instruction to activate or send.
