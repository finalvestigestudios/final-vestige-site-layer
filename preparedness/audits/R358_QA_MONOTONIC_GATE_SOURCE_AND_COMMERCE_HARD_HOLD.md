# R358 — Preparedness QA safety-gate monotonicity and source custody

**Disposition: DRAFT / HARD HOLD / NO MERGE / NO PUBLICATION.** Preparedness Issue #136; conversion coordination #820 / charter #818. This is a read-only reviewer aid, not emergency-safety, clinical, source, privacy, QD or payment approval.

## Exact current evidence inspected 2026-11-13 PT

- Independent safety QA #157 remains an **open draft**. Base `10f58fed1ba808056813064ca5f9680589db8da1`; head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`. Original `preparedness/taxonomy.json` blobs `bd9f8db8821bb0511f3e5b2a75a782373ccf415d` -> `d20ff18bc6f243e08796c0505981979a10fca2d9`.
- Compared actual GitHub source data, not a guessed schema: QA #157 changes **exactly four** article `gate` fields `false -> true`, no other taxonomy property. Article #1 `household-emergency-plan`, #2 `three-day-kit`, #16 `go-bags`, #20 `preparedness-real-households`. Existing gated items increase **18 -> 22** of 35. A `true` gate is a restriction, **not a safety approval**.
- Latest stacked integration parent #2428 / R357 head `67dd810bc8498dfd36aa9a346182df1a360bda2d` retains all **22** restrictions and 35 article identities. Its taxonomy blob is `15c547bb3018ac182b12a51036389cfa39a59168` and lists **nine planned tools**, whereas historical QA #157 had six tool-plan entries. Three extra plans must be preserved and explicitly tracked, not mistaken for authored or published drafts.
- Independent synthetic QA #169 remains **draft** head `e9cd7766dac59d47ab467d8945269b9146c2aef5`. Dependent fixture-fix PR #2205 remains **draft**, head `bbcf1859768624c611df4abadc564c18247cf32a`; no independent QA merge or test/approval authority transfers.
- Homepage integration lead #1689 remains **open draft** head `f55c36b6598eec558dd8bb24e4c8988becc51be0`, outside this lane. Seven Claude contributor branches and two Shelter variants are not altered.

## New boundary / release safeguard

`preparedness/tools/r358_monotonic_gate_hold.py` reads three exact pinned Git taxonomy versions from an existing native checkout, validates immutable identities, 35 article numbers, eight sections, six-to-nine planned tools, canonical route uniqueness, publication-state allowlist, QA's exact four escalation deltas, no downgrade of preexisting article/tool restrictions, and reviewer docket for newly planned tools or editorial status changes. Both byte-level Git blob SHA pins and semantic checking are required in native mode. Reports contain only source hashes/identity metadata and fail closed. No original content, taxonomy, sources, CMS, navigation, offer, tracker or social asset is changed.

The semantic comparator is tested with synthetic fixtures. Its successful review status is deliberately `SOURCE_REVIEW_REQUIRED_HARD_HOLD`, never a QD PASS or a publishing green light. Native entrypoint returns **exit 2 regardless** of any semantic result, to prevent synthetic evidence laundering.

## Test evidence / limitations

- **73/73** individual adversarial Python `unittest` cases PASS locally; source and test Git blob identities are matched against exact committed bytes in this PR. Python compilation PASS.
- Native incomplete checkout test: `INVALID_HARD_HOLD`, **exit code 2**. Local `git ls-remote` to GitHub fails DNS; native complete repository checkout, actual Python `preparedness/tools/validate.py`, actual Python `preparedness/tools/build.py`, full test discovery and 50 WordPress/50 preview build **NOT EXECUTED**.
- CI is not evidenced as passing. Independent claim-level sources, current emergency procedures, child-card privacy, Article #15 / Tool #104 source review and the carried-forward 15 editorial conflicts, 17 priority review obligations, four disputed source identities and duplicated numeric tool metadata require qualified human adjudication.
- The 73 synthetic passes are **not** native full-corpus validation, source verification or WordPress-ready evidence.

## Conversion-first: offer -> funnel -> blocker -> change -> evidence -> owner

| Offer and funnel step | Blocker | Change / acceptance test | Status / owner |
|---|---|---|---|
| Existing FV-owned Preparedness product -> paid order | No independently authenticated rights-cleared active payable Preparedness SKU, delivery/refunds | Founder/Commerce to inspect actual merchant SKU and terms before any paid CTA. Do not invent an upsell. | **UNVERIFIED / HOLD**, Founder/Commerce |
| Free Archive emergency-planning guide -> optional family-contact printable | Detail tool #104 no-JS/privacy/print/child-data restrictions and source review remain open | Preserve free hazard guidance, source lineage and 35-article reading depth; validate actual browser/print, relevant citations, and disclosure with QD; only draft landing copy. | **HARD HOLD**, Preparedness/QD |
| Published Grok family-contact asset -> `/preparedness/` | Published matching asset_id/UTM/allowed destination not authenticated | Grok/Praxxis TASK-008 to supply original post and approved link; no creator queue edit | **UNVERIFIED**, Grok/Praxxis |
| Qualified human sessions -> verified lead -> settled paid receipt -> net revenue | No consented campaign-to-merchant reconciliation, qualified-human denominator, fees/refunds | Claude/Commerce to match only approved event data + merchant paid order and 7-/30-day cohorts; no extra scripts | **NOT COMPUTABLE**, Claude/Commerce |

Proposed **draft-only** CTA: **Start With Trusted Preparedness Resources**, destination `https://finalvestige.com/preparedness/` (existing free landing). Never imply medical/safety clearance, an available purchasable bundle, a paid conversion, or automatic visitor tracking. Do not revive retired water freebies or interfere with the approved Focus lead magnet.

## Approval gates still required

Complete authenticated repo checkout and validation/build; independent reviewer signoff on QA #157/#169/#2205; zero released-source substitutions or citation-loss and validated route/reading-depth parity; qualified source and emergency/child privacy review; confirmation of any merchandised product by Founder/Commerce; founder authorization separately for merge, production releases, social posts, analytics, emails, affiliates, spending and publishing. **No QD PASS is recorded.**
