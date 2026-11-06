# R163 — Family Reunification Card source-scope corrections (review quarantine)

**Owner:** Preparedness Archive source/citation engineering only, Issue #136; business coordination #820 / charter #818. **Status: DRAFT / HARD HOLD.** Parent R162 commit `5fef02a2245cc4773b56db25738fcfaa278bd11d` (draft PR #1220). This work has not been approved, merged, released, deployed, or entered into WordPress. Neither 35 canonical article files, source registers, publication states nor the R159 original Family Card have been altered.

## Substantive editorial remediation

A second *inspectable* draft version is staged at `preparedness/review/r163/family-reunification-card.body.html`, outside the canonical `content/` and builder input. It proposes three additional corrections after R159:

1. **Communications:** Remove the categorical "text messages are transmitted more reliably" attribution to a Ready.gov page that returned HTTP 403. Preserve the exact Ready.gov/FCC citation tokens, acknowledge that voice/SMS may fail, and request a current source verification.
2. **Missing-child service scope:** Describe NCMEC's number accurately while explicitly distinguishing the cited CyberTipline page from a general disaster-reunification service. The CDC's disaster-specific reunification guidance and NCMEC hotline remain separate citations; neither is silently treated as qualified safety review.
3. **FEMA availability:** Remove a potentially misleading present-tense description of national reunification support, because the cited FEMA fact sheet could not be retrieved. Mark current scope/availability unverified, and do not imply that assistance will be available in a particular incident.

**No original reference is substituted or approved.** All **16/16 original citations and their order**, all **11 original source-use interpretations**, identical HTML tag sequence and script/style blocks, and all existing privacy/review caveats are preserved. R163 increases the staged HTML from 19,345 to 19,466 characters. Exact R159 staged HTML Git blob `7a7b6cffbc75cb6c9a0c13ad5002ccf0f5d22ef0`, meta `2bafef03a375b0156e2dcd7f1b913d119becad61`, and R155 observation JSON `9e689fde7e2913340c89886a7fb02994245b60eb` are immutable input pins.

The R155 observation states remain **2 contested source-scope/context, 6 HTTP-403 retrieval restrictions, 3 narrow automated text observations; 11 human decisions pending**. A 403 is never evidence that a URL is dead. The remaining other 64 R153 source-review tasks, including 8 Historical Food citation substitutions, are unaffected (75 total pending). No human reviewer decision has been supplied.

## Validator and testing

`preparedness/tools/r163_family_scope_reconciliation.py` verifies the upstream R162->R161 35-article custody check first, including QA PR #157's safety intentions and synthetic-fixture PR #169/#973 equivalence. It then pins the three source artifacts, verifies all 11 original IDs and outcome classifications still say PENDING, reproduces exactly the quarantined HTML, rejects source/markup/JS/citation/approval drift, and always exits **2**, even on verified structure. It does **not** decide whether any advice is safe.

```bash
python -I -m unittest discover -s preparedness/tests -p 'test_r163_family_scope_reconciliation.py' -v
python -I -m py_compile preparedness/tools/r163_family_scope_reconciliation.py preparedness/tests/test_r163_family_scope_reconciliation.py
python -I preparedness/tools/r163_family_scope_reconciliation.py --repo .
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests
```

**Local isolated synthetic test result:** 61/61 PASS; explicit 44 named adversarial cases plus source-state, missing citation, URL, approval, and HTML-preservation cases. Python compilation passed. **Limit:** the local runner cannot clone this private GitHub repository because github.com DNS does not resolve. Full authenticated R163 integration, native validation/build, 35-article regression, WordPress draft rendering, browser privacy/print/mobile accessibility, human source adjudication, independent safety/QD and actual checkout remain **NOT VERIFIED**. Do not infer production acceptance or independent source verification from synthetic tests.

## Seven contributor branches (GitHub read-only checks, 2026-11-06 PT)

All compared **identical** against R151 recorded exact heads (ahead=0, behind=0), not against every article's original source commit:

| Lane | Branch | Verified current head |
|---|---|---|
| Start | `claude/prep-start-bbfeb8` | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Shelter | `claude/prep-shelter-5e1e0e` | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Food | `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Health | `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Historical Food | `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Historical Home | `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| Historical Field | `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |

Separate unmodified PR heads: QA #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic fixture #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` and #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`; homepage #49 `10495883299d53596992c26a8987f629b2904670` and #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`. No other owner's branch, release or workflow altered.

## Commercial and acquisition boundary

**One high-intent audience hypothesis:** caregivers arranging school pickup and emergency reunification. Grok/Praxxis continue to own TASK-008 asset IDs and creative assets. Proposed free reader path (never a live CTA from this branch): authentic free Household Emergency Plan **DRAFT / HOLD** -> free optional Family Reunification Card **REVIEW / HOLD**. Do not gate essential advice with consent or payments.

**Paid conversion step DISABLED.** There is no authenticated existing rights-cleared, truly purchasable Preparedness SKU with verified checkout, delivery, refunds, or settlements. Do not publish an invented paid pack, misdirect to a poorly matched offer, modify retired water offers, instrument duplicated analytics or imply commercial conversion. Proposed CTA text only: "Build your household contact and pickup plan — free guide." Landing checks before any authorized activation: matching verified Grok `asset_id`, exact approved source URL, mobile readable disclosure, free no-signup access, functional optional printable, consent/privacy QA, independently verified checkout if a relevant product exists. Sessions, CTA clicks, lead confirmations, and paid/refunded orders must remain separate measures. Realized net revenue per 1,000 qualified human sessions is **NOT COMPUTABLE** until source-of-truth merchant orders and qualified-session denominators exist.

**Required reviewer disposition:** independently inspect exact source passages/dates, resolve Colorado and NCMEC scope, manually inspect six blocked official sources, verify print/privacy/accessibility, complete native build and independent QD; founder retains release, posting and spending approvals. No public or CMS writes.
