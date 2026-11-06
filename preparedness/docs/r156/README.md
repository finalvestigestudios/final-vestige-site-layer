# R156 — Frozen-source Family Reunification workorders (DRAFT / HARD HOLD)

**Owner:** Preparedness Archive source/citation gate ONLY, Issue #136; commercialization coordination #820 / charter #818. **Parent:** R155 draft PR #1174, exact parent `d30fe4b1868e3ddcd79596ce32a96834be903d4e`. No original articles, citations, registers, tools, WordPress, CMS, navigation, sales channels or social posts modified. This branch is an incremental **draft**; it cannot authorize release, human source verification, medical safety or independent QD.

## The integration improvement

R154 provides a fingerprinted ledger of **75 pending reviews** (8 Historical Food citations, 67 tool/source relationships, including 11 Family Reunification sources). R155 separately records 11 read-only source observations and 16 citation occurrences. R156 joins these two inventories deterministically, refusing silently missing/duplicated records, changed URLs, source-status upgrades, citation-loss, altered observation classifications or forged QD/merchant approval. It **retains all 64 non-Family workorders**, rather than replacing the parent triage.

The new workorder queue is deliberately **2 disputed-scope/context records → 6 403-retrieval restrictions → 3 narrow text matches still awaiting human source/safety review**. HTTP 403 does not mean dead link. All review states remain pending. Five questions are source-specific:

1. Colorado Office of School Safety: locate and document exact evidence for the attributed photo-ID, pen and limits-on-calls recommendations, or propose a precise correction without silently editing the original article.
2. NCMEC: do not portray the CyberTipline web form as a general disaster-reunification service. Qualify the hotline and seek a context-appropriate source.
3. Ready.gov plan form: do not claim private/local processing, no storage, or no sharing until the current policy has been independently verified.
4. Ready.gov technology: independently check current SMS/service commands and dated guidance before any instructions are repeated.
5. CDC chemical evacuation: preserve hazard-specific scope, not a universal prohibition on going to family.

All eleven workorders require the **exact official URL, title, publication/revision date, page passage/timestamp, original claim in context, hazard/household scope, reviewer identity/date and qualified independent decision** before any source correction request. Do not copy copyrighted source text wholesale. These requirements are reviewer *questions*, not statements of completed verification.

## Source custody and tests

`preparedness/tools/r156_family_review_workorders.py` pins **R154** validator Git blob `96bf1114f75b53413f4d6cbef6fc69a2d81b4294`, **R155** validator blob `2da35a444834579096f491bb3c91d92eb6f8af3b`, and original **R155 observation JSON** blob `9e689fde7e2913340c89886a7fb02994245b60eb`. The pinned R155 validator invokes authentic R149 original citation and source-register verification; R154 invokes the frozen R153 source-review packet chain. The R156 gate does not accept untrusted summary files as replacements for this checkout verification.

Run only in a disposable, trusted full checkout, not against WordPress:

```bash
python -I preparedness/tools/r156_family_review_workorders.py --repo . --report /tmp/fv-r156-workorders.json
# EXIT 2 even for an intact DRAFT_HARD_HOLD; inspect JSON status, NEVER mark QD PASS.
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

**Locally executable results 2026-11-05:** 99/99 R156 isolated Python unittest methods passed; Python compilation passed. Includes 77 source-specific adversarial tests (11 IDs × 7 mutation types), and guards for all-source counts, duplicate task fingerprints, approval injection, Symlink/Git-blob substitution, printed reports, false commercial evidence and preservation of other 64 workorders. Tests are synthetic and **do not mean** that the original 35 articles passed validation/build. The full checkout cannot be cloned here (DNS resolution for github.com unavailable); native validate/build, full regressions, WordPress draft/browser/mobile/print/privacy checks, independent source review, safety and QD remain **NOT EXECUTED / HOLD**. No GitHub Actions re-run was requested or claimed.

## Coordinator handoff — exact observed refs, 2026-11-05 PT

Seven canonical Claude contributor heads checked read-only:
- Start Here `claude/prep-start-bbfeb8`: `2122d856fce9f64887c16df3d52e64be9f59a55b`
- Shelter `claude/prep-shelter-5e1e0e`: `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- Food `claude/prep-food-ccdc55`: `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- Health `claude/prep-health-837444`: `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- Historical Food `claude/prep-hist-food-b81f19`: `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- Historical Home `claude/prep-hist-home-0e0e38`: `7504a5f099594d635e3dd7332a33a2e1346c43a2`
- Historical Field `claude/prep-hist-field-9db767`: `4e5caf812727953aa45e3bda2d382f2c67b6a09c`

Independent QA draft PR #157 head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, synthetic-fixture PR #169 head `e9cd7766dac59d47ab467d8945269b9146c2aef5`, follow-up #973 head `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` remain separate and were inspected, not imported. Homepage PRs #49/#604 are other owners' work. Historical Food eight citation substitutions remain unreleased and await qualified review. No direct content merges, no skipped source safety checks.

## Conversion-first specific funnel — proposed / NOT LIVE

**Audience fit hypothesis:** households with school-age children worried about school pickups, emergency contact chains and reunification. **High-intent social topic:** “If your child's school has to evacuate, who is authorized to pick them up?” Requires creator/safety editorial review and **an actually published Grok asset ID**, not an invented one.

**Free useful destination:** authentic Household Emergency Plan draft, **not yet approved/published as one of the 35**. **Optional practical tool:** source-cited Family Reunification Card (implemented code, but source and print/privacy QA incomplete). **Paid step:** ONLY an existing FV-owned Preparedness SKU after independently verifying product identity, intellectual-property rights, merchant listing and price, fulfilled downloadable bytes, accessibility, refund terms, and source safety. No matching SKU authenticated in this lane; therefore **NO paid CTA and no product URL**. Retired water guide remains excluded. Also do not replace the functioning Focus Fieldbook email workflow.

| Offer → funnel | Highest blocker | Proposed test/change (draft only) | Evidence status | Owner |
| --- | --- | --- | --- | --- |
| Existing paid Preparedness pack → verified purchase | Rights-cleared, actually purchasable SKU not verified | Obtain real merchant listing, checkout, PDF rights/delivery/refund receipts and accessible mobile flow | HOLD / no merchant confirmation | Commerce / Claude / founder |
| Free Household Emergency Plan → engaged reader | 35-article source/safety/QD work and native build pending | Manual reviewer adjudication + no-gate free HTML draft, heading/citation/print checks | DRAFT / NOT VERIFIED | Preparedness + independent QA |
| Free guide → optional Family Reunification Card | 2 disputed, 6 blocked, 3 narrow-match source observations + print/storage concerns | Complete the eleven R156 workorders, test no sensitive family contact data leaves device, print at 360/390/768/1440px | TESTS SYNTHETIC; browser NOT TESTED | Preparedness + Site QA |
| Grok short → free guide | No published Preparedness media ID or approved destination link | TASK-008 reconciliation of real asset_id, platform/post URL, permissions and utm_content; do not change Grok queue | UNKNOWN / NO attribution | Grok / Praxxis / Claude #820 |
| CTA → paid order → net revenue | Qualified-human sessions, consent-safe events, merchant-confirmed orders, fees/refunds unavailable | Existing measurement contract; 7/30-day cohorts; separate outbound clicks, confirmed leads and settled purchases | **NOT COMPUTABLE**, not zero | Growth / Commerce #820 |

**Proposed on-site link label, only after qualified review/approval:** “Create your household communication and pickup plan — free guide.” Optional card label: “Print a family reunification card (draft tool; subject to safety, privacy and source review).” Do not present internal draft labels publicly.

**Campaign-landing acceptance gate (nonproduction only):** exact approved source asset → allowed caption/bio link and immutable media ID; same-intent headline; free guide requires no personal-data gate; article content and citation links survive; card prints legibly with no sensitive storage promises; optional commercial module clearly separated and rights/licence disclosed; active checkout only for approved SKU; no third-party script duplicates; readable at 360/390/768/1440; keyboard/accessibility checks; privacy consent; confirmation of paid order only from merchant settlement; report missing attribution as unknown. No unapproved analytics instrumentation or sales claims.

**Business metric:** realized net revenue per 1,000 qualified human sessions = 1,000 × (merchant-confirmed paid gross less processor fees, refunds and other attributable merchant costs) / qualified human sessions, when denominator > 0 and reconciliation complete. Report 7- and 30-day cohorts, confirmed order count, source asset, paid conversion rate and tiny-sample caution. Never substitute social views, outbound affiliate clicks or newsletter forms for completed paid orders.

**Grok/Praxxis TASK-008 coordination read-only:** shared Drive task and dated handoff checked; no confirmed Preparedness post ID in reviewed handoff. We do not publish, assign Grok's scripts, modify creator content/queue or write the shared Drive. Conversion is strictly gated by authentic offer and source verification.

**Release:** DRAFT / HARD HOLD. No WP/CMS/nav/production merge, email, merchant, affiliate, social post, paid spend or false review sign-off. Founder retains all production releases.
