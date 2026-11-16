# Dispatch R392 independent red-team QA and regression fix

**Release state: HARD HOLD.** This is not live app production code, not a newsletter send, and not a substitute for actual WordPress native email/opt-out review.

## Real source-only bug caught in this sprint and corrected before release
The first `release_gate.mjs` draft iterated `Object.keys(record.attestation)` to verify proof flags. A constructed record that **omitted** nonmerchant keys (e.g., `real_unsubscribe_test`, `physical_address_in_actual_email`, `provider_eligible_recipients`) while setting all present merchant proof keys to true could have reached `can_enter_human_review=true`, even though no permission to actually send was ever granted (`send_authorized=false` was already invariant). This was a **review-eligibility bypass**, not an email-send bypass.

**Fixed**: `REQUIRED_KEYS` is now an explicit 14-field allowlist; every proof key must exist and be strictly boolean true. Omitted fields, absent attestation objects, null, truthy strings and missing nonmerchant checks fail closed. The 4:2 campaign allocation remains immutable, candidate remains NOT_ADOPTED, and no code can set `send_authorized=true`.

Also tightened `confirmedLeadCount`: a static "confirmed" subscriber snapshot no longer counts as a **new signup**. Counting requires a new provider-authoritative `newly_confirmed` transition with privacy-safe opaque subscriber and transition identifiers. Duplicate transitions dedupe, conflicting identities for the same transition fail closed, and raw email identifiers are refused. No provider event data collected or exported.

## Exact-GitHub-source native test evidence
At final new code SHA after `c1894dff66cbc100b7a69728fa8ab1d848ffe4d2`:
- `release_gate.mjs` Git blob: `4d14ffd5006a7d4038c1bd47f18af7284c291ca5`
- `release_gate.test.mjs` Git blob: `9c02fd89e8d22c4b650ffcd889878a15e2046a95`
- `proof_ledger.json` Git blob: `822ebf182f91553b74f59f02451ffa7f09f886d5`
- Independent local `git hash-object` matched all three GitHub SHA-1 blobs, including exact EOF. Native Node v22 command `node --test release_gate.test.mjs` **20/20 tests PASS, 0 fail, 0 skip** (synthetic fixtures only).
- The current original master PR #175 immutable seven issue/manifest blobs separately re-read at exact `d57ccdba3aee8f065e143e101c2945f4f3d01647`; its six original Python assertions were independently reproduced in V8 6/6, **not Python-natively rerun this sprint**. Earlier Dispatch R391 native original Python 6/6 is separately documented.
- Review HTML/static manuscripts have no real Jetpack email MIME/footer/recipient or browser evidence. None of these native source tests proves deliverability or legal compliance.

## Highest-impact remaining blocked proofs
1. Mind/Commerce: named FV publisher acceptance, specific Zen12 SKU and **EMAIL** rights, approved earning link and referred checkout/refund terms, live independently vetted Mind-owned guide.
2. Focus/Founder: eligible recipients (not total followers), double-opt-in/provider status reconciliation, actual received Fieldbook welcome and working PDF link.
3. Dispatch/Founder: **non-sending native WordPress Preview email**, verified sender postal address and operational unsubscribe in native output; separately approve exact creative, audience, dates.
4. Grok/Praxxis/Claude: genuinely already-published content source IDs, legitimate asset/UTM join, audited qualified human sessions, actual merchant-settled commissions and refunds/fees. No invented data, revenue or A/B performance.

No emails or test emails, subscriber imports or contacts, WordPress publication/settings, affiliate activation, Grok queue changes, merges or spending.
