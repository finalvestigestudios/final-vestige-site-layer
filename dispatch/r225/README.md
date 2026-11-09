# Dispatch R225 — merchant-owned opt-in and commercial truth (UNSENT, RESEARCH ONLY)

**Source of truth:** Issue #174 (Dispatch), #171 (Mind & Affiliate), #129 (Focus), #820 (conversion); founder's 2026-11-03 priorities. **Parent:** DRAFT #1684 at `31d5215dda0132b40973eb5d8e115d34609bd730`. This branch does not alter founding PR #175, readiness PR #201, or frozen homepage PR #49.

## New conversion finding
The **exact** Zen12 sales page at https://zen12.com/hnp contains an optional seller-operated free-audio sign-up asking for personal details, saying visitors will receive **the seller's newsletter**, with a skip option. That **merchant-owned list** is not the existing FV Jetpack Dispatch list. A merchant signup must not be attributed to FV as a confirmed lead, paid customer, or independently settled affiliate sale. The page source establishes the offer text, **not** when or whether every visitor sees its modal. No live cross-device merchant checkout or opt-in interaction has been tested.

The exact https://hypnosislive.com/mental-skills/total-focus product page advertises 33 minutes / 47 MB and displays $24.44 next to $29.95. The seller FAQ https://hypnosislive.com/faq lists typical single-session pricing of $22.95 and limits its 14-day refund policy to five sessions annually. These are **seller-page snapshots**, not checkout prices/terms verified for an FV referral. No price or guarantee is inserted into a consumer email.

## Deliverables
- `merchant_evidence_registry.json`: two exact products, merchant assertions labelled unverified, 13 all-false proof references, null commission/sales data, explicit 4 editorial / 2 reserved commercial pilot.
- `merchant_gate.cjs`: offline validator that **never** grants sending permission, even when a synthetic proof object is structurally plausible. No network, account, subscriber or WordPress access.
- `test_merchant_gate.cjs`: thirteen native Node tests with adversarial mutations for fake merchant permission, arbitrary links, vendor email opt-ins, false revenue, altered 4:2 mix and forged attestations.
- `MERCHANT_CONSENT_AND_OFFER_FIRST_AUDIT.md`: the verified source / efficacy / buyer-consent distinction, caveated legal review, owner handoffs and funnel risks.
- `SUBSCRIBER_JOURNEY_NOT_AN_EMAIL.md`: non-sending one-offer progression within the existing six issues, deduplication and cohort measurement.
- `MERCHANT_PERMISSION_REQUEST_NOT_SENT.md`: exact evidence needed from Inspire3 without contacting them.

Execute offline: `node --test dispatch/r225/test_merchant_gate.cjs`. Native local package evidence: 13 of 13 tests passed on byte-identical code and JSON; committed Git object identities for these three files can be compared independently. **Tests are NOT** real Jetpack received-email or merchant-checkout QA, and a source validator is not a legal sign-off.

**Fresh read-only WordPress** 2026-11-09 04:33 UTC: newsletter ON, new-post automatic send OFF, full content mode, sender name Final Vestige Studios, three total/three confirmed/two unconfirmed requests (separate nonadditive counters), welcome with 52-page Fieldbook configured; all five recent posts not emailed. Actual email-eligible population and final welcome receipt remain unknown. A targeted authorized Gmail search found the Oct 25 WordPress confirmation but no named FV Inspire3 EMAIL acceptance or final welcome; absence in that account is not proof none exists elsewhere.

## Release hold
**ALL SIX HOLD_UNSENT. #03 and #05 additionally HOLD_MERCHANT.** No posting, emailing, test emailing, subscriber modifications, WordPress settings, active earning links, tracking deployment, merchant contact, Grok queue writes, spend or homepage changes. Founder retains all creative, recipient, schedule and send approvals. Mind owns merchant acceptance / published buyer guides; Claude owns site engineering; Grok owns social content; Dispatch owns consent/inbox QA.
