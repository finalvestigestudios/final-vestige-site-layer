# R135 — Custody-anchored qualified source and safety work queue (DRAFT / HOLD)

**Scope:** Preparedness Archive only, Issue [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136). Business cross-reference [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). **No publication, CMS, navigation, homepage, production tracking, email, social posting, spending, affiliate activation, or merchant writes.**

**Immutable stacked chain:** R135 starts at R134 draft [#1031](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1031) head `8bcd67a2b14b9c3d91aa817ebe59b3afe2b3fa37`, which stacks on R133 [#1025](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1025) `233ba9876b88508d103c5d7fe13906dd975eabc5`, R132 [#1012](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1012) `5685b54796d520e8dd50e0cdf4d35e38c9cec7a4` and original frozen 35-article RC [#584](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/584) `ddb3528ba6494dada1fa1c3a142ce746e3a67706`. Nothing is merged.

## Added capability — not an approval system

`preparedness/tools/r135_review_queue.py` consumes **only the authentic R134 source-to-passage packet**, which itself requires the complete R133 Git-blob custody audit. It refuses unauthorized statuses, changed article/citation totals, duplicate slugs/block locations, malformed/unresolved provenance and missing exposure of any of the **32 shared-source groups**. It preserves the original **35 draft articles / 2,000 citation-token baseline** without altering a single citation, text passage, source ID, author-specific `source_use`, source crosswalk, taxonomy, draft state, or safety metadata.

Output is deterministic JSON with stable content-and-author-scoped SHA-256 witness IDs for two independent **human** queues: (1) each exposed shared-source group, with its cited variants and exact article/block exposures, and (2) medication, CO/power/fire, water treatment, food preservation, and evacuation keyword-attention passages, sorted for qualified-review triage. Each passage includes exact original citation ID, origin, literal URL, source `supports` wording, author reading scope, verification/link-check fields and source-shadowing flag. A passage without an inline citation is flagged for review; it is **not automatically judged false**. Every task is marked `UNREVIEWED_HUMAN_REQUIRED` and the root result is `HOLD_HUMAN_SOURCE_AND_SAFETY_ADJUDICATION`. Historical `approved` or `not-required` fields cannot become a new sign-off.

**Important limitations:** the task's 20-character display ID is derived from a full SHA-256 witness, but a reviewer must also retain the full `witness_sha256` and frozen parent reference. `cited_variant_identities_only` is **not** a replacement for the R132 crosswalk: reviewers must open each original group and inspect all registered source variants, including any not cited by the packet. Keyword triage is heuristic; qualified reviewers must assess all actionable content, not only flagged passages.

## Command — only on a complete authenticated repository checkout

```sh
python -I preparedness/tools/r133_snapshot_gate.py
python -I preparedness/tools/r134_reviewer_packet.py > /tmp/fv-r134-private-review.json
python -I preparedness/tools/r135_review_queue.py > /tmp/fv-r135-private-human-queue.json
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -p 'test_*.py'
```

**Local exact-source test evidence:** `python -I -m unittest discover -s /mnt/data/r135/preparedness/tests -v` executed **78/78 synthetic/adversarial tests PASS** (35 individual article names plus 43 adversarial/behavioral cases); `py_compile` PASS. The tested local source/test Git blob IDs were cross-checked against the committed GitHub files: source `5a9face97299787727d18525760ccb7b403195b2`, tests `f7df5eb90ce7afe43f6511985e99496286de4132`. These tests exercise synthetic 35-article/32-group fixtures and **are not** the real 2,000-citation checkout execution. Full R133→R134→R135 run, native validate/build, whole-repository 36+ suite, browser, CI and independent QD remain **NOT TESTED / NOT APPROVED**: sandbox DNS cannot resolve github.com to check out the private repo. The connector can inspect GitHub content, not produce an executable local checkout.

## Exact contributor and QA snapshots checked November 4, 2026 PT

| Contributor | Current Git commit (read-only ref) |
|---|---|
| Start Here `claude/prep-start-bbfeb8` | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Shelter `claude/prep-shelter-5e1e0e` | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Food `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Health `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Historical Food `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Historical Home `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| Historical Field `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |

These are **the current heads**, not all equivalent to the older frozen contributor input. Food still diverges from its older release input; the newer Historical Food branch's **eight** `hist-food-nchfp-jerky` → `nchfp-jerky` retargets remain explicitly unresolved decision S-7. R132 retains all 3 source interpretations and 32 pending crosswalk reviews. Independent QA [#157](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/157) `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (electric-drill and refrigerated medication wording) and synthetic fixture QA [#169](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/169) `e9cd7766dac59d47ab467d8945269b9146c2aef5` both remain draft, unmerged. Homepage [#49](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/49) `10495883299d53596992c26a8987f629b2904670` and flagship [#604](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/604) `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176` are untouched.

## Human work priorities and exact gates

1. Qualified source reviewer resolves distinct NCHFP jerky author reading scopes (S-7) in one explicit decision log **without auto-merging IDs**; all 32 shared-source variant groups receive source/passage adjudication. Original source date, current revision, title, quoted supporting section and decision documented; citation occurrence reviewed in context.
2. Qualified emergency/medical reviewer adjudicates the **actual meaning** of competing electrical-drill and refrigerated-medication guidance between R132 and #157 and all other current emergency steps. No such review has been conducted by this script.
3. Independent QD and authorized engineering run native validation/build/whole-suite/real WP draft + mobile/offline browser QA; founder release approval is a separate condition. Do not infer live eligibility from a Python zero exit.
4. Separate website owner reported the **non-instructional Preparedness gateway** at `https://finalvestige.com/preparedness/` as LIVE and added archival cards; **the original 35 instructional articles are still DRAFT/HOLD** under this lane.

## Conversion-first offer → funnel → blocker → proposed change → evidence → owner

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| **Existing FV paid Preparedness practical pack → merchant-confirmed order** | No authenticated existing SKU proven owned, rights-cleared, presently purchasable, fulfillable and suitable; no real purchase/refund record | Commerce owner verifies seller inventory, actual product rights, listing, approved price, checkout and delivered file/refunds; only then stage paid CTA | **UNVERIFIED / HARD HOLD** | Growth / Claude / founder |
| **Free household plan → qualified reader** | Source and safety checks and 35-article release gates incomplete | Adjudicate citation exposures, obtain qualified safety review, validate reader-visible references and mobile/print | **DRAFT / HOLD** | Preparedness + independent safety QA |
| **Grok asset → relevant landing visit** | TASK-008 does not identify an actual verified Preparedness asset ID, post URL or approved link route | Grok/Praxxis supply actual immutable `asset_id`, post URL, placement and `utm_campaign`; Claude/Site QA confirm working destination and consent | **UNVERIFIED / NO LAUNCH** | Grok / Praxxis / Claude |
| **Free guide → optional free family-reunification printable** | Existing printable mobile, accessible print and private-local-data behavior not tested | Staged only; verify phone/keyboard/print, no upload of household contacts, correct disclosure | **NOT TESTED** | Preparedness / Site QA |
| **Purchase → realized net revenue per 1,000 qualified humans** | No verified attributed merchant transactions, fees/refunds or session denominator | Use existing #820 measurement contract: asset → human session → CTA → confirmed lead (if applicable) → merchant paid order/affiliate settlement → fees/refunds; 7/30-day cohorts, tiny-sample caveat | **N/A / NOT COMPUTABLE, not zero** | Growth / Claude |

**Draft CTA, NOT published:** “Make a family contact plan you can actually practice. Read the free Household Emergency Plan, then use the optional family-reunification worksheet to record contacts and pickup arrangements.” No speculative product, price, checkout URL, water freebie or unapproved affiliate. No essential safety instruction behind a signup.

**Governance:** no PR merge, no CMS/WordPress writes, no changes to Grok's creator queue or TASK-008, no analytics duplications, no false medical safety or QD PASS, and no revenue claims.
