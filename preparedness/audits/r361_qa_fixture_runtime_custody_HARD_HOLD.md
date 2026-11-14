# R361 — PR #169 / dependent #2205 synthetic-fixture runtime custody
Status: DRAFT / HARD HOLD / NO PUBLICATION
Issues: #136 (Preparedness), #820 (revenue measurement), #818 (founder charter).
Base: R360 draft PR #2443, commit `1fa9ee12b2db8b217c7cce7b6ced5896273c0ccb`.

## Exact original QA evidence
- Independent synthetic-fixture QA PR #169 head `e9cd7766dac59d47ab467d8945269b9146c2aef5`; its `preparedness/tests/test_preparedness.py` Git blob `e80d622c2fd32bf6c9752e375c1208c1d47d8e7c`. It is NOT an independently approved fixture implementation.
- Dependent remediation PR #2205 head `bbcf1859768624c611df4abadc564c18247cf32a`; corrected test blob `b63e7f4dc9c84a4bef15dd581affe08ac81356af`. **These are separate draft PRs; remediation must be reviewed into #169 before the latter can be considered.**
- Pin exact candidate test bytes. A baseline #169 file, changed contents, missing runtime guard, missing TemporaryDirectory/source copy, or missing test cases produces INVALID_HARD_HOLD.
- Never run fixture tests against their canonical checkout. For candidate-native execution, copy the whole Preparedness tree into a temporary sandbox, run four exact fixture/negative cases only under isolated Python, and compare full source fingerprint manifests before/after for both original and copied trees. Reject changed, deleted, added, linked, or oversized source files.
- Exit code 2 **in every case**. Even successfully witnessed synthetic tests remain REVIEW_REQUIRED_HARD_HOLD, not qualified safety/source approval, native WordPress parity, or merchant proof.

## Reproducible local synthetic testing
```sh
python -I -m unittest discover -s preparedness/tests -p 'test_r361_qa_fixture_hold.py' -v
python -I preparedness/tools/r361_qa_fixture_execution_hold.py --repo-root .
```
- **52/52** new isolated synthetic Python tests executed locally against byte-identical committed tool and tests; Python compilation PASS.
- Tested exact successful sandbox (still HARD_HOLD), malicious mutation of copied original source, exception from fixture test, missing checkout/dependencies, source drift, duplicate/unsafe sources, symlink/hash changes, invalid code and success-state prevention.
- Candidate-native execution: **NOT EXECUTED**; container cannot resolve github.com for a complete authenticated checkout. The explicit missing-checkout path exits 2 / INVALID_HARD_HOLD.
- Do not interpret test executions as 35-article / six-authored-tool complete validation. Full repository validate/build, 50 private WordPress and 50 noindex preview files and independent CI/qualified QD remain **NOT VERIFIED**.

## Nine pinned original contributors, source continuity
`claude/prep-food-ccdc55` `f911ff7a655de8d81535ea86ec3d65a49ee76648`;
`claude/prep-health-837444` `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`;
`claude/prep-hist-field-9db767` `4e5caf812727953aa45e3bda2d382f2c67b6a09c`;
`claude/prep-hist-food-b81f19` `67e116e536c7410bed30f8f3b1bb8c166f3c223d`;
`claude/prep-hist-home-0e0e38` `7504a5f099594d635e3dd7332a33a2e1346c43a2`;
`claude/prep-shelter-5e1e0e` `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`;
`claude/prep-start-bbfeb8` `2122d856fce9f64887c16df3d52e64be9f59a55b`;
`claude/prep-shelter-continuation` `ac8625faf30dd5538fadc31e06cb5a2cea1defae`;
`claude/prep-shelter-followup-evidence` `6a5998ead97eca997e573ce8d3ceacf1c6aabad4`.
All ten original and QA #169 branches compared against their pinned ref and returned `identical` on 2026-11-14. Remediation R318 head `bbcf...` checked identical. No branch rewritten.

## Safety and conversion action
The existing public `https://finalvestige.com/preparedness/` explicitly promises official resources free without signup/purchase; do not gate them. Candidate social intent: a *verified published* Grok family-communication/school-reunification asset -> public free household emergency-planning agency link -> optional practical download ONLY after content/source/privacy/no-JS/print approvals. Tool #104 remains private; Article #15 stays safety-held. Preserve 22/35 QA-escalated safety flags, source occurrence crosswalk and 15 editorial conflicts / 17 high-priority obligations / 4 disputed source identities.

**Offer → Funnel → Blocker → Change/experiment → Pass/fail → Owner**
1. Existing rights-cleared payable Preparedness pack → merchant paid order → SKU, purchase, delivery, rights, fees/refunds unverified → Commerce authenticates merchant and delivers a test receipt (no live test purchase without approval) → HOLD → Founder/Commerce.
2. Free agency-linked planning guide → optional printable → Tool #104 unresolved source/citation, child privacy, no-JS and print risks → qualified review and offline/browser/print QA before any link → HARD HOLD → Preparedness/QD.
3. Published family-contact social asset → Archive → no verified Grok `asset_id`, platform link or permitted UTM destination → Praxxis independently verifies exact published post + mobile route, without changing Grok's queue → UNVERIFIED → Grok/Praxxis.
4. Qualified-human sessions → CTA → confirmed lead (if any) → settled order → realized net revenue per 1,000 / 7- and 30-day cohorts → native tracker, receipts/refunds and identity linkage unavailable → no conversion claims → NOT COMPUTABLE → Claude/Commerce.

No new paid SKU, retired water freebie, tracking vendor, purchase, email, CMS/nav/public publishing, social posting or Grok production change. Human QD and founder release decisions remain separate.

## Required next checkpoint
Authenticate full repository + PR #2205 checkout on exact SHA. Run R361 native witness there, R360 composite gate and `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, `python -I -m unittest discover -s preparedness/tests -v`; independently review all source citations and inspect all 100 private exports before any release decision. All unmet gates remain HARD HOLD.
