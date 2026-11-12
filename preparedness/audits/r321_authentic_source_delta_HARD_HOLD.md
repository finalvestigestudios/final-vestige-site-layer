# R321 — Authenticated three-way source-delta review (DRAFT / HARD HOLD)

**Date:** 2026-11-12 · **Owner:** Preparedness integration and source/citation safety, Issue #136; conversion coordination #820/#818.

**Governance:** No merge, public publishing, CMS/navigation/source changes, tracking deployment, merchant activation, posts, email, or spending. No independent QD, child-privacy, qualified medical or emergency-safety approval.

## Authenticated source crosswalk

The R321 source-delta receipts (groups 01–03) cover all 15 R320 unresolved source records: **45 remote Git file fetches** (15 integrated, 15 Shelter continuation, 15 Shelter follow-up). Every returned Git blob SHA and actual UTF-8 byte length matched the frozen R320 docket source pins, Git blob 3119626a19175cec8f0dc4f03c5da57f319906d0. All 15 entries retain UNRESOLVED_HOLD. The 54 integrated-only and 13 identical overlaps remain recorded in R319, with no automatic source selection.

- Group 01: family communication, home fire, water-filter metadata (15 fetched blobs).
- Group 02: water-safety, generator/outage guidance, historical salted meat, shelter/evacuate (15 blobs).
- Group 03: shelter metadata, power-outage planner and reunification-tool identity (15 blobs).

## Material source findings

**Reunification:** The continuation replaces the integrated plan-builder with an object 4,933 characters longer; follow-up is 5,400 longer. The replacement removes five heading occurrences and adds six, with **17 detected form-control tags versus zero** in integrated HTML, and changes multiple citation-like bracket tokens. Metadata changes title, h1, n, dek, description, related, tags, source_use and recheck. It is not a safe automatic replacement of tool #102, and the separate family-reunification-card identity must remain intact.

**Shelter/evacuate:** Continuation is 497 characters shorter than integrated; follow-up 133 longer; source_use and related routes differ. **Family communication:** Continuation is 574 characters shorter and follow-up 117 longer; source_use and related routes differ. Heading parity does not prove warning or advice parity.

**Power outages:** Generator/heat/cold article variants add 101 and 128 characters, and continuation source_use differs. Power planner continuation is 473 characters shorter; follow-up body is source-identical to integrated, with 86 detected form controls in both bodies. Continuation source_use differs. Qualified CO, evacuation, medical-device, print and child-privacy reviews remain required.

**Approval ambiguity:** Making Water Safer and historical salted-meat metadata change safety_review. Home-fire metadata differs in raw Git identity even though parsed top-level key values match; whitespace-level differences do not authorize source replacement.

The authenticated receipts record syntactic differences only, not claim-level medical or life-safety correctness. Bracket-token differences are citation-like lexical evidence, not independent source authority, visible citation or QD clearance.

## New R321 source gate and tests

The read-only Python gate requires the complete R319/R320 pinned source/docket and Git object store, uses local git cat-file on exact SHA-1 blob identities, checks length and UTF-8, then computes human-review deltas for headings, links, citation-like tokens, form fields and metadata paths. Duplicate JSON keys, changed blobs, missing objects and bogus release state fail closed. No auto-merge or approval state is possible.

**Local:** 95 new R321 synthetic adversarial cases PASS; 198 inherited R319/R320 cases PASS; **293/293 Python tests PASS**; Python compilation PASS. Both locally executed R321 source/test files match the newly committed GitHub blob identities. Incomplete native checkout correctly returns INVALID_HARD_HOLD/exit 1.

**Not verified:** Authentic native validator/build, all 41 WordPress/41 preview exports, qualified claim safety/child privacy review and independent QD. Local full checkout unavailable because GitHub DNS resolution fails; the new delta gate's full real-Git-object CLI has not been executed.

## Independent QA and conversion-first acceptance

PR #157 remains draft. QA #169 retains a canonical-source duplicate-fixture write; remediation #2205 is separate and still needs reviewer integration. Homepage lead PR #1689 remains untouched.

**One household-contact/reunification audience.** Existing official-source public archive is the free reference candidate; Grok/Praxxis must verify a previously published matching asset_id, permitted UTM, intent and signed-out mobile destination. Original Article #15 and Tool #104 remain hard-held. No verified FV-owned/licensed, purchasable, deliverable matching Preparedness pack, therefore **no paid CTA or sales assertion**. Claude/Commerce must reconcile merchant-confirmed orders, refunds, fees and 7/30-day attribution before revenue per 1,000 qualified sessions can be calculated.

Owners: Preparedness/QD (source review), Grok/Praxxis (social asset and landing intent), Claude (site, measurements, checkout), Founder (release and spending).
