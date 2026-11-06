# R162 — Independent QA PR #157 and synthetic fixture PRs #169/#973 reconciliation

**Preparedness only | Issues #136 and #820 | DRAFT / HARD HOLD.** Parent R161 commit: e7d1eabf6210460c6f3b35e9f8a32235e795844d. Original 35 articles, 2,000 citations and 385 author-source relationships unchanged. R162 adds files only; nothing has been merged, approved, or published.

## Actual three-way result (authenticated read-only inspection, 2026-11-05 PT)

**Independent QA #157** (head 7d1ae6b8ef93d10cfb6810987672360885e9c1aa) is against an older Start Here base. Its previously unsafe main-power-off drill is superseded in the canonical household-emergency-plan body (Git blob f81cd43516e8295104230412f18776919148f905). The current wording proposes simulated outage practice, forbids switching off the main breaker for a drill, and identifies refrigeration, alarms, sump pumps and critical medical equipment. It is not independent electrical safety approval. Its refrigerated medicine wording is superseded by a more extensive currently drafted source-uncertainty discussion (three-day-kit Git blob 933f38ff3cd55a241cf9b392014fc52d4961e84f), citing start-fema-power-sheet and start-ready-power with advice to consult a prescriber/pharmacist, but no qualified medical review has been completed. Do not cherry-pick the older QA patch or restore the old discard instruction.

The Red Cross source classification is already nonprofit in the current start source fragment (blob 96140d6d1872588e5d20d9052445c9157e88934d), while human_link_check remains false. This is not proof of independent source adjudication. Canonical taxonomy (blob 15c547bb3018ac182b12a51036389cfa39a59168) contains 35 unique slugs and all four Start Here safety gates.

**Fixture PR #169** head e9cd7766dac59d47ab467d8945269b9146c2aef5 and its follow-up **#973** head 4d40996a559b0124d74a9bb3bdcd481ad1992aa8 have their key synthetic-source test isolation behavior already present in the canonical test_preparedness.py (blob c329f98e051d2aabe31a3343869b0fdac355b315). Upgrade and duplicate-ID tests work in TemporaryDirectory copies, while the unverified-source test uses an in-memory synthetic source. Both PRs remain separate drafts; this is not an approval or a claim that their commits were merged.

## New deterministic gate and local tests

R162 adds a fail-closed, read-only QA-rebase validator. It first invokes R161 full 35-body custody, pins five canonical Git blobs, checks safety qualifier and source classification presence, and verifies source-fixture isolation test structure. Any drift returns INVALID_HARD_HOLD. Matching frozen inputs return DRAFT_HARD_HOLD; the CLI always exits 2. It never authorizes publishing, medical safety or independent QD.

**55 of 55 isolated synthetic Python tests passed locally; Python compilation passed.** Committed Git blobs were verified against locally executed files: gate 388dcd0e2843e172c3f3015eab6624bc8c07f567; tests 450166aef28716216feca49932ff51ccbabb7909.

Trusted checkout commands (NOT executable locally because github.com DNS resolution fails):

    python -I -m unittest discover -s preparedness/tests -p test_r162_qa_rebase_gate.py -v
    python -I preparedness/tools/r162_qa_rebase_gate.py --repo .  # expect exit 2; inspect JSON
    python -I preparedness/tools/r161_body_custody_gate.py --repo . # expect exit 2
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

The native 35-article build, full integration regressions, independent content/source/safety review, browser privacy/print/mobile tests, and QD remain **NOT VERIFIED**. None of the 75 pending source-review decisions, including eight Historical Food citation substitutions and eleven Family Card sources, have been resolved.

## Exact contributor checks

Seven Claude branch heads rechecked identical to previous recorded SHAs (ahead 0 / behind 0):
- Start Here 2122d856fce9f64887c16df3d52e64be9f59a55b
- Shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976
- Food f911ff7a655de8d81535ea86ec3d65a49ee76648
- Health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17
- Historical Food 67e116e536c7410bed30f8f3b1bb8c166f3c223d
- Historical Home 7504a5f099594d635e3dd7332a33a2e1346c43a2
- Historical Field 4e5caf812727953aa45e3bda2d382f2c67b6a09c

Homepage PRs #49 (head 10495883299d53596992c26a8987f629b2904670) and #604 (head bdf01b4a3e13fd6179ae9e847c9d4429bbe16176) checked and untouched.

## Conversion-first mandate — draft plan, not live

High-intent audience: households with school-aged children making emergency contact, school pickup and family reunification arrangements. Grok owns creator/video output; Praxxis independently QA's the shared TASK-008 inventory. No verified Preparedness-specific published asset_id, platform post URL, approved exact destination URL or attributable session exists in the reviewed handoff.

Proposed free flow: an **ungated Household Emergency Plan** (original draft) to an **optional free Family Reunification Card** (R159 quarantined review draft, unresolved privacy, printing and 11 sources), then an **optional verified existing rights-cleared purchasable Preparedness product**. No matching paid SKU, checkout/delivery or refund evidence has been authenticated. No paid CTA enabled; no retired water freebies, no changes to the existing Focus Fieldbook offer.

Draft CTA, NOT approved for publishing: **Make your family contact and school pickup plan — free, no signup required.** Keep all essential safety instructions accessible without providing personal data.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Existing Preparedness pack → merchant purchase | Matching owned, rights-cleared purchasable SKU unverified | Verify existing product/rights, checkout, fulfillment, refunds before any paid CTA | HOLD / no transaction evidence | Commerce/Claude/founder |
| Free Household Plan → reader | Source, safety, native build and QD outstanding | Source adjudication and staged mobile/accessible article test | DRAFT / no source or medical approval | Preparedness/QA |
| Guide → Family Card | 11 source issues; privacy/print untested | Review R159 wording, print/privacy/accessibility in browser | HARD HOLD | Preparedness/Site QA |
| Grok post → landing | No authenticated Preparedness asset ID or destination | Reconcile TASK-008, preserve Grok ownership/queue | UNVERIFIED | Grok/Praxxis |
| Merchant purchase → realized net revenue | No qualified-human denominator or paid merchant truth | Reconcile consent-safe 7/30-day sessions, orders, fees, refunds | NOT COMPUTABLE, not zero | Commerce/Growth #820 |

Landing acceptance before any public change: exact verified Grok asset_id/UTMs and allowed platform link; same-intent headline; ungated guidance/citations; 360/390/768/1440 and keyboard checks; privacy and print tests; truthful claims and source dates; no duplicate analytics; properly disclosed, approved optional paid offer; merchant-confirmed sale only after settlement. Net revenue per 1,000 qualified human sessions must include fees/refunds and small-sample warnings.

**No WordPress/CMS, navigation, homepage, analytics, merchant, affiliate, email, social posting, paid service or spending changes. Release remains founder-controlled, independent QA/QD required.**
