# R340 — Deterministic 100-file source-to-render custody (DRAFT / HARD HOLD)

Scope: Preparedness Archive ONLY, issue #136; commercial acceptance #820; charter #818. No publishing/CMS/social/analytics/merchant operations.

## Why this gate matters
R330 checks pairwise parity between WordPress and private preview. R339 checks rendered links and warnings. Neither alone establishes that paired exports derive unchanged from source: a synchronized edit to both paired files may pass those controls.

R340 independently regenerates in memory every one of 41 article/tool documents, eight section hubs and one landing, using the frozen authoritative source, original builder and CSS; then compares every one of the 100 expected WP/preview HTML bytes to on-disk output. It also crosschecks report's ordered source IDs, word counts, canonical routes, hub coverage, landing card count and draft state.

The check requires R339 genuine native preflight (which requires R338, R337, R336 and R330 custody), and independently pins the source builder to Git blob 349173d1e1d735eade218d95c7a0a2649c8cccd9 and CSS to e354395cdb7985eb2fe16b99ca9fd66c9885557e. Code never invokes builder main, write_lf or CMS writes.

One-byte mismatch, synchronized WP+preview tampering, missing/extra export, false publication state, source mismatch or invalid checksum -> INVALID_HARD_HOLD.

## Verification limitation
Only isolated synthetic fixtures can execute with local DNS outage. 114 newly added adversarial cases + 875 inherited isolated cases = 989 local Python tests, pending verification against the exact committed file bytes. The genuine native 50+50 export build, source rebuild and hosted CI are NOT VERIFIED. A passing fixture is always DRAFT_HARD_HOLD, never qualified safety review, independent QD PASS or release authorization.

Article #15 and family wallet Tool #104 remain privately held with 17 source/safety/privacy review obligations and 15 independent integration editorial conflicts. E334's 2013 FEMA master-plan vs fold-over carry-card distinction also remains human review work and is not merged as safety-approved advice. Tool #102 has a distinct identity.

## Conversion gate
One proposed high-intent audience: household emergency-contact and reunification. Only proposed public free destination is the pre-existing agency-source Archive, once Grok/Praxxis independently verifies a published matching social asset ID and permitted mobile URL. No authenticated rights-cleared, actually payable/deliverable FV Preparedness pack; no approved paid CTA, publisher conversion or net-revenue claim. Founder reserves approval; Claude owns production site analytics; Grok owns social production. No retired water offer or other changes.
