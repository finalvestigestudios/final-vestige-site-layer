# Preparedness R462 — exact-source shared-URL/reading-scope custody

**2026-11-18 PT. DRAFT / HARD HOLD.** Preparedness Archive only: Issue #136, commercial issue #820, founder charter #818. No edits to authored content or live systems. Structural provenance never proves emergency/medical/food advice safe.

## Authenticated frozen inputs

- Parent R461 draft #3009 HEAD: f007c2dcb609f0d849a273049d53917cb5fa1ae8.
- R460 original nine-contributor, 35-article snapshot Git blob: 056d14cd97d29b843d52912383c237b9122e73ef.
- Existing source crosswalk Git blob: d62e493a67dedd23e04cfdf3cce762ef933c6bf9.
- Exact current Git blob identities of **all eight** source files matched the crosswalk's frozen file roster. None of the 75 crosswalk identities is orphaned.
- Independent QA #157 HEAD 7d1ae6b8ef93d10cfb6810987672360885e9c1aa and fixture #169 HEAD e9cd7766dac59d47ab467d8945269b9146c2aef5 were directly inspected, left unchanged. QA #157 has bounded safety wording/taxonomy fixes; #169 isolates synthetic food-test fixtures; neither grants source or QD approval.

## Exact currently authored source census

| Metric | Count |
|---|---:|
| Authored source rows across original 8 files | **244** |
| Distinct literal source URLs | **202** |
| Shared-literal-URL groups | **32** |
| Groups with distinct reading-scope strings | **32** |
| Groups with different source IDs | **18** |
| Groups with at least one empty reading scope | **15** |
| Groups with differing verification dates | **20** |
| Groups still marked pending-human-review | **32** |
| Frozen source files that match current Git blobs | **8 / 8** |

The 32 groups in the current exact-source crosswalk are **not** the same denominator as the 17 historical shared-URL review groups in an earlier separate integration audit. Do not erase either register or infer that one supersedes the other. The separate five semantic source disputes, nine manuscript/source forks, 17 article divergences and four changed source fragments remain HARD HOLD.

## Code, tests and verification boundary

The new R462 read-only gate independently rebuilds shared URLs from individual authored source rows, matches source ID, origin, original row index, full source record, publisher, reading scope, verification fields and all URL group memberships. It requires frozen Git blobs for the actual crosswalk/source files, the nine-origin and 35-article snapshot, rejects silent URL retargeting, source-identity collapse, missing groups, altered scopes, duplicate JSON keys, unsafe reviewer state and linked evidence. **No URL normalization/deduplication is permitted as editorial approval.**

The committed R462 suite defines **57 separately named synthetic tests**, including **49 hostile mutation methods**. Structural test success must not be called qualified source, emergency, medical, food or QD PASS. A complete authenticated local checkout is required for the native integration build and WordPress/private-preview gate. R462 CLI always exits 2 even if the structural inventory is intact, preventing publication automation from treating its result as an approval.

Suggested commands from an authenticated exact PR checkout:
- python -I -m py_compile preparedness/tools/r462_shared_url_scope_custody.py preparedness/tests/test_r462_shared_url_scope_custody.py
- python -I -m unittest discover -s preparedness/tests -p 'test_r462*.py' -v
- python -I -m unittest discover -s preparedness/tests -v
- python -I preparedness/tools/validate.py
- python -I preparedness/tools/build.py
- python -I preparedness/tools/r462_shared_url_scope_custody.py

No actual source-to-claim human adjudication, 35-article native build, private WordPress export, qualified safety or QD approval is asserted.

## Conversion-first acceptance — one real offer, not a hypothetical product

| OFFER → FUNNEL | BLOCKER → CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|
| Authenticated FV-owned Preparedness paid toolkit → merchant-confirmed order | Verify payable SKU, seller/rights, delivery, refunds/fees, settlement BEFORE any paid CTA | HOLD, no verified qualifying SKU | Founder / Commerce |
| Published matching Grok family-contact asset → free official guide | Praxxis independently verify actual asset ID, date/permalink, exact hook, rights and mobile link; do not seize Grok queue | UNMATCHED | Grok / Praxxis |
| Free official planning guide → optional separate printable Tool #104 | Article #15 source claim, child privacy, emergency, accessibility and print review; keep #102 separate | HARD HOLD | Preparedness / QD |
| Qualified-human UTM/asset_id sessions → relevant CTA → confirmed lead where applicable → paid order → net revenue | Reuse Claude's existing consent/privacy-reviewed measurement; verify actual orders, fees/refunds, 7/30-day cohorts and tiny-sample caveat | NOT COMPUTABLE, verified transaction evidence absent | Claude / Commerce |

Unpublished free-only CTA candidate: **Review the official household emergency checklist.** Verify its official destination and mobile behavior before any use. Never resurrect retired water freebies or imply traffic/clicks/leads are paid sales.

**Release state: DRAFT / HARD HOLD.** No merge, CMS or navigation write, public publication, social post, email, analytics deployment, affiliate/merchant activation, expenditure or false QD PASS.
