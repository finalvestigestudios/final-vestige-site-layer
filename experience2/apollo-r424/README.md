# Apollo R424: authentic-template Research Desk acceptance

**DRAFT ONLY. Production HARD HOLD.** This isolated QA harness never writes WordPress, changes homepage PR #49, modifies Research Desk PR #158 or Grok/Praxxis TASK-008, or activates commerce and analytics.

The previous R423 browser tests used a synthetic source-ledger shape. R424 replaces that assumption with a **fail-closed real-source acceptance runner**, pinned to PR158 commit 250d7f05a4de037e73826dcf0cfaef0ec4c29383 and R423 commit 93dda51158453fbc8e2fcc353ef535490eac0d73. It verifies three exact Git blobs from PR158 plus the exact R423 PHP adapter, including symlink escape rejection. Only then does it render the actual R423 shortcode twice with PHP staging stubs and exercise unique IDs, six records per instance, source custody, a single free investigation CTA per instance, and independent search interaction.

To run from this directory:

    python qa/test_runner.py
    python qa/real_research_desk_acceptance.py --repo /read-only/pr158-checkout --bridge-dir /read-only/r423-folder --output QA/real-template

The Playwright suite covers 320, 360, 390, 768, 1024, 1440 and 1920px, keyboard, no-JS, forced colors, reduced motion and reproducible screenshots. **Actual PR158 source was unavailable locally during R424; authentic integration therefore returned HOLD, exit 2.** Five adversarial custody tests passed. The local browser runtime rejects HTTP navigation, so genuine axe-core, navigated LCP/CLS and installed WordPress staging are NOT VERIFIED. R417's earlier four-file identity mismatch also remains a release blocker.

Source: NASA Apollo 204 Review Board, https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . The ignition initiator was not conclusively determined. No NASA imagery, insignia, fictional map pins or geographic edges are introduced.

## Offer → funnel → blocker → experiment → evidence → owner

| Offer | Funnel step | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|---|
| Original Apollo educator kit | Verified paid order | No verified rights-cleared live SKU/fulfillment | Withhold purchase CTA | HOLD | Founder / Claude |
| Grok Apollo documentary | Qualified human visit | Approved published asset_id/UTM not verified | Use existing TASK-008 without changing queue | UNVERIFIED | Grok / Praxxis |
| Apollo Research Desk | Trust to free investigation | Previous tests used synthetic source HTML | Exact-source QA runner | 5/5 custody unit PASS; authentic integration BLOCKED | Apollo / QD |
| Confirmed order | Net revenue per 1,000 human sessions | Orders, fees/refunds and 7/30-day cohorts unknown | Measure only through approved verified systems | NOT COMPUTABLE | Claude / Commerce |

Proposed path: verified Grok Apollo video → source-backed Research Desk → free investigation at https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ → separately approved, rights-cleared, genuinely purchasable teacher kit. No unapproved commercial CTA, content publication, spending or instrumentation.

Cross-reference GitHub issues #150 (experience), #820 (measurement), #818 (business). Release requires actual staged installation, source reconciliation, exact-head CI, independent QD and founder approval.
