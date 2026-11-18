# R454 — Contextual citation-anchor integrity review (DRAFT / HARD HOLD)

**Scoped ownership:** Final Vestige Preparedness Archive, Issues #136 and #820 only. Parent: R453 draft PR #2967 at \`69f95c3fa1be978a1bfd5213d56de4ff86ac9261\`. No source/citation decisions, manuscript selection, WordPress changes or commercial release are authorized by this PR.

## Why this additional gate is necessary

R453 detected source and reading-depth changes and counted citations per source ID. Equal counts can still hide a different claim being cited. R454 makes the **surrounding claim unit** part of the review identity: (source ID, heading context, HTML unit type, normalized visible text, SHA-256). For every changed source/claim association it reports removed/added short contextual excerpts, source ID, local original source URL/scope fingerprints when the ID belongs to the pinned Start Here fragment, and counts before/after.

It preserves repeated citation occurrences instead of deduplicating them. It flags changes even if overall count and source ID counts are unchanged. Citations in tables, list items, and nested formatting are parsed; citations outside a supported visible claim unit, malformed citation placeholders, unbalanced supported units and source-pin mismatches are rejected rather than silently skipped. Unknown IDs outside the Start Here fragment are **not** falsely declared orphaned: they require full-register lookup. Reports do **not** determine whether the linked source actually supports the medical, food, generator or child/privacy advice.

## Exact source and agent custody checked 2026-11-17 PT

- Original R397 docket blob \`86d22a1d504c93db7689b914e2202a7845b648e2\` read from \`a22c8797da58ecf186f50fcf47063bd195fd3c17\`: **35** identities, **203** original source IDs, **280** source occurrences, **181** literal URLs, **17** shared-URL groups; 5 source disputes and 9 manuscript/source forks remain **UNSELECTED**.
- All **7 Claude branch heads + 2 Shelter descendants** were freshly resolved by GitHub at their exact nine R397 frozen SHAs; 9/9 matching, no automatic resolution.
- QA #157 draft \`7d1ae6b8ef93d10cfb6810987672360885e9c1aa\`; synthetic fixture #169 draft \`e9cd7766dac59d47ab467d8945269b9146c2aef5\`; dependent #2205 draft \`bbcf1859768624c611df4abadc564c18247cf32a\`; none modified or merged.
- Home-lead draft #2931 \`c43980270e3e9d31c03fcb70e0f1126914c58604\`; Article 11 editorial #2789 **advanced** to \`fb7435e7e78d7d38c5e2d9d4f39eccd785b136e8\`. No overwrite or cross-lane edit.
- Authenticated QA #157 article-body Git blobs: \`6407a31a882211e62c00f4e07ec7dc4d5abf99c6\`, \`f578cdbae602c1ad58a9237c8dea0fd74c99f7da\`. Corresponding later R451 body blobs: \`f81cd43516e8295104230412f18776919148f905\`, \`933f38ff3cd55a241cf9b392014fc52d4961e84f\`. These are pinned by R452 and inherited by this tool.
- A **separate limited paragraph-only exploratory read** of actual original GitHub snapshots found household-plan citation counts 57→57 (37 paragraph citations each) and three-day-kit 68→79 (33→38 paragraph citations). Four source IDs had paragraph-context changes in the latter; this is *not* complete contextual Python execution against originals and does not cover citations in list/table blocks.

## Executable evidence

- New exact-byte committed Python module and 73 synthetic test methods: **73/73 PASS** locally, Python compilation PASS.
- Combined local R452+R453+R454 synthetic tests: **227/227 PASS**; inherited modules/tests were taken from the earlier archived local R453 artifact. This is regression evidence only.
- Original full 35-article native \`python -I preparedness/tools/validate.py\` and \`python -I preparedness/tools/build.py\`: attempted in the limited local assembly; both exit **2** because those canonical files/full checkout are absent. No actual WordPress/private-preview export, browser accessibility check, full-register citation trace or qualified source/safety/QD review has executed.
- Reproduce **after authenticated full checkout and reviewer-provided original snapshots**, outside canonical source directories:
  \`python -I preparedness/tools/r454_claim_anchor_integrity.py --qa-root /tmp/qa157-snapshot --candidate-root /tmp/r451-snapshot\`
  The CLI enforces original SHA pins by default. Do not replace these with synthetic pins for real editorial custody.
- Reviewer needs to inspect **every changed claim-to-citation association**, verify each official claim against the exact current source/page and documented scope (including the CDC infant and HUD multifamily reading-scope changes), resolve the five source disputes, nine forks and 17 shared-URL groups, then perform real private build/export, device QA and qualified QD review. Never map automatic textual consistency to advice safety.

## Conversion-first owner matrix — ONE tentative audience, zero unverified paid offers

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| **ONE existing FV-owned/licensed genuinely purchasable Preparedness pack** → paid checkout | No authenticated seller rights, SKU, checkout, delivery entitlement, price/refunds/fees | Read-only verify ownership and independently merchant-confirmed payable SKU and end-to-end delivery before any paid CTA | **HOLD / NOT VERIFIED**; no speculative sales link | Founder / Commerce |
| EXISTING published on-topic Grok family-contact/reunification asset → free landing | Immutable asset_id, post URL/date, hook, rights and permitted mobile CTA link **UNMATCHED** | Praxxis independently QA's already-published asset; Grok retains production/posting ownership; do not create tasks | **UNMATCHED**, no fabricated UTM or attributed visits | Grok / Praxxis |
| Existing free Preparedness Archive → source-backed official guide | Current Ready.gov link accessibility, original Article #15 caveats, child privacy, mobile link navigation incomplete | Unpublished free-only CTA candidate: **“Review the official household emergency checklist”**; verify live agency destination and mobile consent/trust | **DRAFT / HARD HOLD** | Preparedness / QD |
| Optional distinct practical Tool #104 download | Separate Tool #102 identity, emergency instructions/child privacy/print accessibility and safe data handling unreviewed | Stage as clearly optional **only after** qualified review; keep free emergency information ungated; no sales claim | **HARD HOLD / NOT RELEASED** | Preparedness / QD |
| Unique real asset_id → qualified-human sessions → landing → CTA → confirmed lead → settled paid order → refunds/fees → **net revenue per 1,000 qualified sessions** | No independently verified asset/session denominator, attributable confirmed purchases/settlements or 7/30-day cohorts | Review Claude-owned native measurement, avoid duplicate scripts, privacy/consent and mobile checkout; separate visits, clicks, leads and paid sales | **NOT COMPUTABLE**, no revenue claim | Claude / Commerce / Founder |

**Release state: \`DRAFT_HARD_HOLD\`.** Nothing in this work is LIVE or VERIFIED commercial conversion. No merge, WordPress/CMS/navigation edits, public post, email, creator queue overwrite, analytics deployment, merchant activation, spending or false QD PASS.
