# R460 source provenance and numbered-tool collision review
Issue #136 · Business #818 · Conversion #820 · DRAFT / HARD HOLD / NO PUBLICATION.

Parent R459 exact HEAD: 9b4846d2b2a94f7aeee2689e9b738f94a9eab97a. Fresh nine original/descendant contributor refs, their Git-tree blobs, 35 article pairs, six tool pairs, one original hub body (83 content files), and seven source fragments plus register (8 source files) are recorded in r460_original_branch_provenance.json. Its exact blob: 3b50fe91423c7dbebe336550ca5fb9256b8bd356.

## P0: two real duplicate numeric tool identifiers — BLOCKED
Original R459 frozen tool metadata identifies:
- ID **102**: home-fire-escape-worksheet (metadata blob 397c7d3072fb237b490a5a316c93fc863c101be9) AND reunification-plan (10cd57dc8d39e366aaef8fd76cc3f8969b8c5348).
- ID **103**: kit-builder (e9be8a497df737b36d7d399fccc4a00000ce8eac) AND power-outage-planner (8796bba2b323cce096639997002c402bd853e50f).
- ID 101 water-planner and ID 104 family-reunification-card are unique; 105 and 106 are unused.

These are **numeric ledger collisions, not demonstrated duplicate canonical URLs**. All six are distinct draft slugs, status draft, safety review pending. No automatic renumbering, redirect or CMS write. Qualified owner must choose stable original identities and update related source/audit/URL references without losing any tool. The R460 validator intentionally HOLDS against the present uncorrected original metadata; do not report native PASS.

## Reconcile actual article/body branch evidence, not just test counts
Fourteen of the 35 integrated article body blobs do not exactly match any one preserved contributor snapshot: family-communication-plan; go-bags; home-fire-escape-plan; household-emergency-plan; navigation-before-gps; outage-heat-cold-generators; pemmican-and-dried-meats; pioneer-supply-chains-failed; pioneer-travel-rations; preparedness-real-households; root-cellars-cool-storage; sanitation-before-germ-theory; shelter-or-evacuate; three-day-kit.

Six content bodies have distinct contributor-branch blob variants: the four articles family-communication-plan, home-fire-escape-plan, outage-heat-cold-generators and shelter-or-evacuate, plus power-outage-planner and reunification-plan tool bodies.

A transformed blob does NOT prove content loss; a matching blob does NOT establish source safety. Review complete original paragraphs, citation contexts, caveats, source IDs and human review states before selecting versions. Preserve independent historical docket: 5 source disputes, 9 editorial source/manuscript forks and 17 shared-URL review groups (not interchangeable with the 6 body-blob variants here). QA PR #157, fixture #169, repair #2205 remain independent unmerged drafts.

## Verified local scope and native runbook
Synthetic local Python tests cover 35 original article-body corruptions, altered source register, duplicate 102/103 tool identities, branch-head drift, noncanonical source/metadata, unsafe status claims and symlinks. Python compile and isolated regression only; no native repository build, authentic dual exports, qualified medical/emergency/food/privacy/QD authorization or commerce validation.

From an authenticated complete checkout:
1. python -I preparedness/tools/validate.py
2. python -I preparedness/tools/build.py
3. python -I -m unittest discover -s preparedness/tests -p test_r460*.py -v
4. python -I preparedness/tools/r459_full_draft_surface_custody.py --root preparedness
5. python -I preparedness/tools/r460_original_branch_provenance_gate.py --root preparedness --live-refs /path/to/fresh-nine-ref-shas.json

The optional live-ref input must contain nine freshly fetched key-to-SHA values matching the manifest, independently verified by the reviewer. Without this, the CLI reports NOT_RECHECKED_IN_CLI rather than asserting verified. A changed ref causes HARD HOLD. No rebase, merge or public export from this check.

## Conversion-first owner contract
1. ONE genuine existing rights-cleared FV-owned Preparedness SKU -> paid checkout. Blocker: no seller rights, checkout/fulfillment/refund, settlement and approved SKU proof. Change: founder/Commerce authenticates before considering any paid CTA. Evidence: HOLD; no commercial activation.
2. ONE verified already-published Grok family contact/reunification asset -> existing ungated https://finalvestige.com/preparedness/. Blocker: real public asset ID, exact hook, creator rights, permitted working mobile link not matched. Praxxis independently checks; Grok retains production/posting. UNMATCHED; do not fabricate UTM.
3. Official household planning resources -> optional unpublished Tool #104. Blocker: Article #15 source/911 claims, child privacy, accessible mobile and print review. Qualified safety owner/QD only. HARD HOLD; Tool #102 stays distinct.
4. Qualified-human landing -> CTA -> confirmed lead -> merchant-confirmed paid order -> realized net revenue per 1,000 qualified sessions, 7/30-day cohorts. Blocker: actual attribution and settlement/fees/refunds missing. Claude measurement / Founder commerce. NOT COMPUTABLE, not zero.

Draft CTA only: "Review the current household emergency-planning resources." Existing free public Archive destination; no new paid CTA, upsell, subscriber gate, retired-water freebie, or creator task.

No publishing, WordPress/CMS/navigation changes, email, social posts, creator queue edits, analytics or merchant activation, spending, QD PASS, or net revenue claim. Founder retains production-release and commerce approval.
