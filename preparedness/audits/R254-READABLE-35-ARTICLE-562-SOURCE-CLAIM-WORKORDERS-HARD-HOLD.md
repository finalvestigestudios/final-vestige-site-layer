# R254 — Reader-visible source/claim review workorders (DRAFT / HARD HOLD)

**Scope:** Preparedness Issue #136; founder conversion priority #820 and charter #818. **No merge, release, CMS, navigation, social, creator queue, merchant, analytics, spending or publishing rights are implied.**

## Problem and improvement
R253 linked the 32 unresolved shared-source groups to citation ordinals and cryptographic context hashes, but its matched-citation records did **not contain the actual human-readable surrounding authored text**. Reviewers needed to hunt down each source occurrence manually or risk treating a digest as claim evidence. R254 creates a **read-only reviewer docket** that restores the exact R237 authored context excerpt for each R253 matched occurrence, alongside article number, article slug, citation ordinal, original source ID, source URL, source-use note SHA-256 and unresolved review state.

The new independent gate recomputes R237's per-article occurrence-array SHA-256, verifies the complete R253 receipt SHA-256, matches the claimed source ID and contextual hashes across the two independently authenticated receipts, detects duplicate/foreign citation mappings, and enforces the separately observed static census **35 articles / 2,000 citation occurrences / 32 shared groups / 56 distinct source IDs in those groups / 562 overlapping source-ID occurrences / 1,438 other citation occurrences**. That static census was independently confirmed by Praxxis on 2026-11-10 02:58 UTC and is not a source-support or reading-safety certification.

The three originally disputed citations are explicitly located at **Article 7 citation ordinals 30 and 48 (cdc-find-clean-water)** and **Article 20 ordinal 55 (start-ready-plan)**. Each remains marked pending. This control blocks ambiguous claim reordering, silent safety/QD approvals, deleted groups, and citation loss. Other 1,438 citations are **not approved**, only outside this particular duplicate-URL review cohort. No original text, citation, route, metadata, safety state, producer code or source register is edited.

## Tested engineering scope
- R254 stand-alone module: `preparedness/tools/r254_readable_claim_workorders_hold.py`; Git blob `76d5030cd774c1474e2d0b69510045ed404fe8fd`.
- R254 test suite: `preparedness/tests/test_r254_readable_claim_workorders_hold.py`; Git blob `4f8b694f7a7413386d4e378378a7dafdc66acdd1`.
- **78/78 isolated synthetic Python tests PASS**; Python compilation PASS. Confirmed GitHub blob identities match the locally executed files. Tests include adversarial input approval flips, corpus/group drift, unreadable claim witnesses, forged excerpt hashes and duplicate/lost citations.
- R220 now invokes pinned R254 immediately after authenticated R235/R237/R253 receipts and **before draft export**, checks the hard holds and rechecks R254 module identity at end of audit.
- **NOT EXECUTED:** complete native validate/build/inherited suite, end-to-end real R220/R254 receipt generation, WordPress-ready 41-export verification, real browser/print, original claim source reading and independent QD. Full `git clone` fails in the local runtime due to GitHub DNS resolution; the GitHub connector can retrieve individual authenticated files. Do not represent isolated synthetic success as native QA.

## Editorial and commercial holds
Source scope for all 32 groups is unresolved; the three CDC/Ready.gov citations need qualified human review. Article 7's creek chemical-contamination warning should be assessed for an unambiguous **do-not-treat/stop** boundary by a qualified reviewer, not mechanically altered. Article 15 / Tool 104's six-field minimal card disclosure, no-JS fallback, printed data exposure and privacy wording also remain held. No assertion that advice is medically safe.

**One provisional conversion hypothesis:** an existing authenticated Grok video about keeping emergency family contact/record information organized (not yet identified) leads to the **existing ungated** `https://finalvestige.com/preparedness/` free guide. Existing Legacy Triage PDF is **NOT APPROVED** as an upsell: full product rights, suitability, checkout, privacy, delivery, refund and founder sign-off remain unknown. Never introduce an unapproved offer, retired water freebie or invented creator asset.

| Offer → funnel step | Blocker | Change/experiment | Pass/fail evidence | Owner |
| --- | --- | --- | --- | --- |
| Real Grok asset → existing free guide | Published matching asset ID/date/rights/mobile URL unknown | Verify within existing TASK-008, no creator queue edits | UNVERIFIED | Grok / Praxxis |
| Free guide → detailed sourced reading | 32 groups / three disputed citations / native build held | R254 readable claim docket + independent source review | BUILT / SYNTHETIC TESTED / RELEASE HOLD | Preparedness / QA |
| Free guide → printable family card | Privacy and JS-off contradictions | Approve editorial behavior/disclosure and real browser/print tests | NOT APPROVED | Editorial / QA |
| Free guide → optional Legacy Triage | Actual product suitability, rights, sensitive-data policy unresolved | Full downloadable-file review, founder gate | NOT APPROVED | Commerce / Founder |
| Optional pack → paid order | Merchant confirmation, fulfillment and refund evidence unavailable | Authorized checkout/delivery verification, 7/30-day reconciliation | NOT TESTED | Commerce |
| Qualified human sessions → net revenue | No attributed confirmed sales or reliable denominator | Source-aware paid-order/fees/refund reconciliation, not outbound-click proxies | NOT COMPUTABLE | Analytics / Commerce |

**Publication, merchant, claim-source, medical and independent QD approval remain FALSE.**