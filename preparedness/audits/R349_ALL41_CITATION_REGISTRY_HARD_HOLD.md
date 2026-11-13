# R349 — Full 41-document citation occurrence ↔ frozen source identity join

**2026-11-13 PT | #136 / #820 / #818 | DRAFT / HARD HOLD / NO PUBLICATION**

This is an additive, read-only Preparedness integration gate stacked on R348 PR #2382 HEAD `8582038506b7f20c4988a95546f29d65e2f65fc3`. No canonical author manuscripts, 35-article slate, six tools, source fragments/register, taxonomy, safety state, URLs, WordPress, navigation, analytics, commerce or Grok creator queue are modified.

## Engineering improvement

R348 established an accurate in-body disputed-source occurrence parser (17 occurrences across ten original private drafts). R349 extends that approach to the **entire 35-article + six-tool slate**, joining each citation occurrence to an original registered source identity, source URL hash and exact authored semantic-region hash, plus its metadata declaration hash. The return value is a deterministic **redacted reviewer docket**: no original claim text, named household/contact details or raw merchant links.

- Preserves authored citation order and multiple mentions per paragraph (distinct ordinals).
- Makes metadata-only source declarations visible **without** counting them as actual in-body support.
- Rejects missing/duplicate body–metadata pairs, duplicate canonical document identities and cross-type slugs, non-draft or invalid safety states, unregistered citations/declarations, incomplete registries, source collisions, unverified research records and unproven human-link flags.
- Rejects symlinked content directories or source pairs and detects falsified/truncated source metadata.
- Requires exact preceding R348 Git blob `98d083b7ec202a2e467863419398e5814747b714` and R344 Git blob `4d9b562c72c13c8a1fd71fd1f2129571b8d35dbf`, plus R348's own predecessor custody chain and identical counts. Always exits CLI code 2, including when a clean draft docket can be generated.
- **Neither a research `verified_on` date nor a matching URL nor test success is a human source check, independent claim support, medical/emergency advice approval, QD PASS or authority to publish.**

## Verification / limitations

- **Local isolated/reconstructed:** 79 new R349 synthetic tests PASS, 238 total after adding R344/R348 reconstructed tests (all PASS), Python byte-compilation PASS. The final committed GitHub R349 code and test files are **not byte-identical to the locally reconstructed/executed files**; do not call this exact-commit or native green CI.
- Incomplete native checkout returns **`INVALID_HARD_HOLD`, exit 2**, by design. The genuine complete repository validation/build/unit suite and the private 50 WordPress + 50 preview artifacts have **NOT BEEN EXECUTED OR VERIFIED**. Local container cannot resolve GitHub DNS; connector readbacks are not a full checkout.
- Original R344 findings remain **244 source records / 225 distinct IDs / 4 disputed research-verified identities**; R348's original source readback found **17 literal disputed citations** across **ten** originals. R349 does **not** newly authenticate the full 41-entry original citation count and does not adjudicate any of those four competing sources.
- Nine Claude/Shelter source branches compared 2026-11-13 PT to original pinned exact SHAs: all reported **identical, 0 ahead, 0 behind**. QA #157 `7d1ae6b8...` and #169 `e9cd7766...` remain open draft; dependent #2205 `bbcf1859...` unmerged; homepage lead #1689 `f55c36b6...` unchanged.
- **15 original contributor conflicts**, **17 Article #15 / Tool #104 claim/child-privacy holds**, and the four source-identity conflicts remain unresolved. Tool #102 plan builder remains separate from Tool #104 wallet card.

## Conversion-first scope / acceptance

| OFFER → FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT / PASS EVIDENCE | OWNER |
| --- | --- | --- | --- |
| Existing FV-owned Preparedness pack → verified paid order | No verified rights-cleared payable SKU, genuine checkout, digital delivery or refund evidence | Authenticate seller rights, completed merchant orders/refunds/fees; **HOLD / no paid CTA** | Founder/Commerce |
| Public free archive → relevant family-contact guide and optional wallet card | Original Article #15 / Tool #104 held for emergency and privacy review | Qualified claim-by-claim QD + keyboard/mobile/print safety; **HARD HOLD** | Preparedness/QD |
| Published Grok family-contact asset → free official agency archive | No independently authenticated `asset_id`, post URL, permitted mobile destination | TASK-008 owner-provided exact asset ID / URL / campaign evidence before routing; **UNVERIFIED** | Grok/Praxxis |
| Qualified-human visit → relevant CTA → confirmed lead / merchant order | Attribution, consent and merchant records unavailable | Existing owner measurement only, separate 7/30-day cohorts, settled receipts less fees/refunds; **NET REVENUE NOT COMPUTABLE** | Claude/Commerce |

Candidate free CTA only, not deployed: **Start With Trusted Preparedness Resources** → https://finalvestige.com/preparedness/ . Do not revive retired water freebies or assume unapproved packs are sellable.

## Release decision

**OPEN / DRAFT / HARD HOLD**. No merge, public publishing, CMS/nav write, social post, creator queue modification, email, analytics script, merchant or affiliate activation, spend or false QD safety clearance. Next: authenticate entire native repository and 100 private rendered outputs, run committed 61-case GitHub suite plus inherited locked tests, and obtain qualified adjudication for the four disputed source identities and original claim/conflict docket.
