# R182 — Semantic reconciliation of safety and fixture PRs (DRAFT / HARD HOLD)

**Owner:** Preparedness Archive #136. Business / conversion coordination #820 and charter #818. **Stacked on R181 exact commit** `1062eb2c775bed8c061fa853d25bc954c28c9529`. No production, merge or safety-approval authorization.

## Why this integration gate exists

R181 identified that QA PR **#157** and fixture PRs **#169/#973** overlap in `preparedness/tests/test_preparedness.py`. Rather than cherry-pick unrelated bases, R182 compares the **actual R181 resolved tree** with the intended safety and test isolation invariants. Authenticated GitHub reads found the current R181 original source already carries **semantically equivalent (and locally more detailed)** no-main-breaker practice guidance, medicine-storage clinician/pharmacist cautions, correct American Red Cross nonprofit classification, four Start Here safety gates and temporary isolated source-test fixtures. The original files are **not copied, rewritten or prematurely approved**.

R182 pins the **five exact Git blob hashes** of the two safety-sensitive bodies, Start Here source fragment, full taxonomy and original regression test suite. Its read-only Python gate checks that the safety wording stays in the **containing HTML block** (not a footer), modern drafts retain gates, source type cannot quietly become 'regulator', and the original source-fragment mutation tests use isolated `TemporaryDirectory` sandboxes. It rejects source drift, missing provenance, duplicate slugs, injected merchant redirect, unsafe test writes and missing original negative tests. It delegates the seven-branch and #157/#169/#973 PR-state admission to the inherited R181 gate and always returns **exit code 2** (`DRAFT_HARD_HOLD` or `INVALID_HARD_HOLD`).

## Exact authenticated GitHub intake, Nov 7 UTC

| Original R181 source | Original Git blob SHA |
| --- | --- |
| `household-emergency-plan.body.html` | `f81cd43516e8295104230412f18776919148f905` |
| `three-day-kit.body.html` | `933f38ff3cd55a241cf9b392014fc52d4961e84f` |
| `start.json` | `96140d6d1872588e5d20d9052445c9157e88934d` |
| `taxonomy.json` | `15c547bb3018ac182b12a51036389cfa39a59168` |
| `test_preparedness.py` | `c329f98e051d2aabe31a3343869b0fdac355b315` |

Seven Claude branch comparisons were freshly checked and returned **identical / 0 ahead / 0 behind** against the seven exact SHAs recorded in R181's `contributor-evidence.json`. PR #157 remains open/draft at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5`, and #973 at `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`. The latter is stacked on #169. Current homepage PR #1326 was inspected at `36888bea912c4dafad16d8dd96b059ff164b6350`; homepage was not touched.

**Important distinction:** source-content equivalence is **not** an authorized merge of PR #157/#169/#973. Original PR review and any separate source correction decisions remain pending.

## Executed versus still blocked

- Locally compiled the **exact two newly committed Python files** and ran `python -I -m unittest discover -s preparedness/tests -p 'test_r182*.py' -v` in an isolated synthetic checkout layout: **68/68 PASS**, including **51 independently reported mutation cases**, with no skips. GitHub blob IDs of committed files were compared with tested local bytes.
- Using authenticated GitHub-read source text, separately inspected 8 specific semantics across the original five files: localized no-breaker warning, localized medication warning, CDC medication citation, nonprofit classification, 35 taxonomy entries, 35 unique slugs, all modern gates, and isolated source-fragment fixtures. **8/8 structural source observations**, NOT native Python execution or independent factual/safety review.
- `git ls-remote` in the local Python container continues to fail with **Could not resolve host: github.com**. Full original repository checkout, authentic `validate.py`/`build.py`, combined complete test suite, WordPress output, qualified safety-source judgments, QD and browser/print/privacy QA remain **NOT EXECUTED**.

Trusted-checkout preflight (intentional exit code 2 is a hold, not success):
```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r181_contributor_intake_gate.py --observed preparedness/review/r181/contributor-evidence.json
python -I preparedness/tools/r182_semantic_patch_reconciliation_gate.py --repo . --output /tmp/fv-preparedness-r182-hold.json
```
Maintain source-adjudication gates R170–R180, rendered citation custody R174–R176, the R177/R178 warning/admission policies and original 35-article prose. No QD PASS can be inferred from a structural match.

## Conversion-first single-audience lane (not activated)

**High-intent audience:** caregivers organizing school pickup and family reunification when phones are unavailable. Proposed social hook: “Who can collect your child if the phones fail?” → **unpublished/held** free Household Emergency Plan → optional **held** Family Reunification Card printable. Free core emergency safety content remains ungated. The existing **Seven Day Focus Fieldbook** at `/focus/` is the current free signup flow, not a new Preparedness offer. Do not revive retired water freebies.

**Paid bridge remains blocked:** No independently verified, currently purchasable, rights-cleared matching FV Preparedness toolkit/SKU; no confirmed checkout, deliverable licensing, refund/fee policy, or approved purchase URL. Do not add a buy CTA or advertise a new SKU. Grok/Praxxis TASK-008 remains the canonical source for an actual creator asset ID, public post URL, allowed caption/bio link and exact campaign destination; these are still unverified. No Grok queue edit, post or new script.

**Funnel priorities / owners:**
1. Existing rights-cleared Preparedness SKU → verified purchase: **HOLD**, merchant/listing/delivery/refund evidence missing; Commerce/Claude to authenticate before any CTA.
2. Grok caregiver media → free plan: **UNVERIFIED**, no asset ID or matching published URL; Grok/Praxxis to supply through TASK-008.
3. Free plan → optional Family Card: **HARD HOLD**, 11 source decisions, privacy, accessibility and print QA; Preparedness + independent Site QA.
4. Landing visit → CTA → independently confirmed lead/order → refunds/fees → net: **NOT COMPUTABLE**, qualified-human session and confirmed merchant transaction evidence unavailable; Claude/Analytics/Commerce under #820. Use 7/30-day cohorts, no click-as-sale counts.

Draft (unpublished) CTA: “Who picks up your child if phones fail? Read the free Household Emergency Plan, then create a family contact and reunification plan.” Staged acceptance must verify content match, no data leakage or tracking in printable tools, keyboard and screen-reader interactions, 360/390/768/1440 layouts, readable paper output, true download availability, source/current safety checks, and accurate no-purchase pressure disclosures.

**Governance:** no merge, CMS write, public navigation, live publishing, email/social posting, affiliate activation, duplicate measurement, spending or founder approval assumption. This branch is source-only and draft.
