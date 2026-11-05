# R133 — Reader-visible citations integrated into the exact Preparedness release candidate | DRAFT / HOLD

**2026-11-04 Pacific.** Scope: Preparedness Archive Issue #136; conversion priorities #820 and charter #818. **Branch:** `integration/preparedness-r133-visible-citation-rc-hold-20261104`, based on exact R132 source-alias PR #1012 head `5685b54796d520e8dd50e0cdf4d35e38c9cec7a4`; underlying 35-article candidate #584 remains `ddb3528ba6494dada1fa1c3a142ce746e3a67706`.

## Integration lift: a tested research branch's protection now enters native RC validation

Previous R122 draft PR #955 introduced a read-only HTMLParser check for citation markers concealed in HTML comments, data attributes, scripts, and invisible content. That gate and its synthetic test suite were **not wired into the actual RC's `validate.py`**, so a nominal citation count could still pass while a footnote marker was not reader-visible.

R133 copies the original `preparedness/tools/r122_reader_visible_citation_gate.py` and `preparedness/tests/test_r122_reader_visible_citation_gate.py` **byte-identically from #955**; GitHub blob SHAs match originals:
- gate: `31d0c67b4aec62a317f5c619b77e82f6a6b2af44`
- tests: `52924dc51e378a46bafc7141400cbc88b1ff1590`

The exact-RC `preparedness/tools/validate.py` now checks raw vs ordinary visible HTML text-node citations **before** resolving any citation tokens into footnotes. Hidden/comment/attribute/script citations and malformed markers produce explicit article errors and block validation. A new full-slate regression module checks all 35 original article drafts independently, retains article-specific source-use references, tests the historic jerky author scope, and tests in-memory hidden/malformed mutations against native validation.

**No original article, taxonomy, source register, crosswalk, source-use explanation, safety classification or WordPress draft/page was edited.** Existing 32 source-alias human-review HOLD groups and S-7 historic jerky identity decision remain untouched. Static visibility does **not** prove reader CSS visibility, rendered accessibility, claim accuracy, medical/food/electrical safety, or source reading depth. Browser and human review remain required.

## Evidence obtained in this run, with precise limits

All 35 actual candidate article body blobs were independently fetched from GitHub on the new branch. Each had the same frozen RC body object SHA, and all citation-token openers matched the permitted literal source-ID pattern. Counts by consecutive article groups: #01–09 = **467**, #10–18 = **670**, #19–27 = **422**, #28–35 = **441**. **Total = 2,000 occurrences in 35 bodies; 0 malformed raw openers observed in this independent token census.** This is a structural census, not a browser-visibility test, source review or safety signoff.

The imported R122 module defines **62 synthetic/adversarial unittest cases**. The new R133 integrated module defines **43** additional cases: 35 numbered original-article checks and eight further parser cases plus four baseline/in-memory integration checks. **105 test cases are committed/defined, but NONE are claimed as executed on this exact head in this environment**. The container cannot access the private repository; `git ls-remote` returned `Could not resolve host: github.com`. The native `validate.py`, `build.py`, entire Python suite, WordPress-ready draft output, staging browser checks, GitHub Actions at this head, independent QD and qualified human source/safety review are **NOT VERIFIED**. Prior R122 test claims are historical, not a rerun.

Reproduce in a trusted **full** repository checkout (all original and candidate Git objects available):

```sh
git fetch origin integration/preparedness-r133-visible-citation-rc-hold-20261104
git switch --detach origin/integration/preparedness-r133-visible-citation-rc-hold-20261104
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I -m unittest preparedness.tests.test_r122_reader_visible_citation_gate -v
python -I -m unittest preparedness.tests.test_r133_release_candidate_visible_citations -v
```

The offline builder is for **local WordPress-ready DRAFT files only**. No WordPress/CMS or public publish/navigation writes, no CI/QD-pass claim, no safety or source approval, no email, social publishing, merchant activation, analytics instrumentation, or spending. Do not merge until independence, qualified adjudication, and exact-head tests are complete.

## Current seven-branch and QA reconciliation checked on 2026-11-04 Pacific

| Contributor | GitHub-resolved current SHA | Decision |
|---|---|---|
| Start | `2122d856fce9f64887c16df3d52e64be9f59a55b` | frozen source retained |
| Shelter cluster original | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` | frozen source retained; separately pending follow-up |
| Food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` | diverged; no automatic merge |
| Health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` | newer docs held for review |
| Historical Food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` | S-7 source-ID collision held |
| Historical Home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` | newer article variations require three-way adjudication |
| Historical Field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` | newer variations require review |

Separate shelter follow-up branch `claude/prep-shelter-followup-evidence` currently resolves to `6a5998ead97eca997e573ce8d3ceacf1c6aabad4`; it is NOT the frozen seven-cluster shelter head above.

Draft QA PR #157 remains `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; divergent household electrical-drill and refrigerated-medication language needs qualified independent adjudication. Fixture PR #169 remains `e9cd7766dac59d47ab467d8945269b9146c2aef5`; standalone unmerged fix #973 addresses the last shared working-tree test fixture. Release candidate #584 is still draft at `ddb3528b`. Homepage #49 (`10495883299d53596992c26a8987f629b2904670`) and homepage #604 (`bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`) have independent owners and were untouched.

## Conversion-first Preparedness path — do not invent sales

One proposed high-intent social topic: **a household communication and child school-pickup/reunification plan that people actually rehearse**. Existing free destination: `/preparedness/start-here/household-emergency-plan/` **only if URL/current publishing status and independent article safety approval are verified**; currently DRAFT/HOLD. The existing family-reunification printable is an optional free tool, also held pending safety, accessible-print and sensitive local-data handling review. Proposed draft nonpublic CTA: **“Put your family’s emergency contacts and meeting places in one practical plan. Read the sourced household guide free—no signup required.”**

TASK-008 shared Drive and dated Praxxis/Grok handoff were inspected. No authenticated Preparedness-specific posted Grok `asset_id`, publish date/permalink, allowed click path, and confirmed destination was established. Grok retains production/posting; Praxxis coordinates their existing handoff. Do not change their queues, repurpose their platform metrics as site visits, or activate links.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| **ONE** actually purchasable FV-owned Preparedness SKU → paid transaction | Seller ownership/rights, real listing, price, refunds, download fulfillment not authenticated; unrelated third-party Payhip products do not qualify | Growth/Claude obtain exact authorized merchant evidence, file/delivery proof, then draft optional accurate upsell; keep CTA absent until approval | **HOLD / no FV SKU verified** | Growth + Claude; founder commercial release |
| Free household guide → qualified reader | 32 shared-source reading scopes, #157 emergency guidance and native validator/browser QA pending | Run exact-head validation/build, qualified citations/safety review, responsive/print tests at 360/390/768/1440 px | **DRAFT / NOT SAFETY APPROVED** | Preparedness + independent QA |
| Grok actual social asset → approved landing | No verified matching actual `asset_id`, URL or platform destination | Grok/Praxxis TASK-008 provide authentic IDs, campaign/source, URL and link-placement restrictions; Claude staging attribution QA | **UNVERIFIED** | Grok / Praxxis / Claude |
| Guide → optional free practical download → optional paid pack | Printable not reviewed; paid pack not authenticated | Check free download semantics, print contrast, privacy of filled-in family/medical data, consent, no misleading outcomes; require real paid SKU before commerce link | **DRAFT ONLY / PAID CTA DISABLED** | Preparedness / Site QA / Growth |
| Qualified sessions → CTA → confirmed lead where applicable → independently verified orders → net revenue | No approved attributable campaign or merchant order/refund/fee ledger | Use existing consent-aware data; distinguish clicks/leads from purchases; report 7/30-day cohorts, denominator and small samples | **N/A (not zero)** | Growth / Claude |

**Primary commercial KPI:** realized net revenue per 1,000 qualified human sessions = **not computable**. No claimed revenue, conversions, approved affiliate link or validated checkout.

**Release state: HOLD.** Source-review integrity improved in a separate, nonpublic draft branch. All original 35 articles and original author reading depth must remain intact until human source/safety decisions, trusted repository tests and independent QD release clearance.
