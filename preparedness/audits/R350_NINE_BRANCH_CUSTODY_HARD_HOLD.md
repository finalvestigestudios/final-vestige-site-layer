# R350 — nine-branch, 41-document source-custody reconciliation gate

**2026-11-13 PT · Preparedness Issue #136 · conversion Issue #820 · charter #818**

**DRAFT · HARD HOLD · NO PUBLISHING · NO MERGE AUTHORIZATION.**

## Scope and new gate

Stacked on R349 draft PR #2387, commit `e8558565c92f3cb3e7133cc68196c46e6604d8ea`.
Additive read-only Python integration tool `r350_nine_branch_content_custody_hold.py` and adversarial tests. No change to original body, metadata, source fragments, safety states, URLs, WordPress, navigation, homepage, Grok queue or merchant code.

The tool pins **seven original Claude cluster branch heads plus two Shelter descendants**, reads only their local Git tree objects without checking out or modifying a branch, and makes a deterministic SHA-redacted reconciliation docket. It rejects drifting/missing/unpinned branch refs; missing body/metadata pairs; duplicate document identities or verified canonical URL candidates; non-draft/safety-state elevation; undeclared citation IDs; empty bodies; metadata/slug mismatch; and unsafe, credentialed, query-string, traversal, scheme-relative or malformed URL candidates. It identifies competing manuscript hashes, citation order, source-use sets, metadata/safety/URL variants and word-count ranges across branches **for human selection**. It never automatically merges a winner or equates reading depth with byte count.

Nine pinned original heads (verified by GitHub ref API on Nov 13, 2026):
- `claude/prep-food-ccdc55` `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- `claude/prep-health-837444` `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- `claude/prep-hist-field-9db767` `4e5caf812727953aa45e3bda2d382f2c67b6a09c`
- `claude/prep-hist-food-b81f19` `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- `claude/prep-hist-home-0e0e38` `7504a5f099594d635e3dd7332a33a2e1346c43a2`
- `claude/prep-shelter-5e1e0e` `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- `claude/prep-start-bbfeb8` `2122d856fce9f64887c16df3d52e64be9f59a55b`
- `claude/prep-shelter-continuation` `ac8625faf30dd5538fadc31e06cb5a2cea1defae`
- `claude/prep-shelter-followup-evidence` `6a5998ead97eca997e573ce8d3ceacf1c6aabad4`

## Verification scope

- **68/68 synthetic adversarial Python tests PASS** in isolated local filesystem, with exact executed source/test Git blobs matching this PR's committed blobs. Python compilation PASS.
- Incomplete native checkout returns `INVALID_HARD_HOLD` and CLI exit code 2, never publication PASS. Full repository native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, complete unit suite and authentic 50 WordPress + 50 preview files **NOT EXECUTED** (container's GitHub DNS failed). Hosted CI **NOT VERIFIED**. No genuine nine-branch corpus reconciliation output is claimed.
- Independent QA PR #157: draft head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic QA #169: draft head `e9cd7766dac59d47ab467d8945269b9146c2aef5`; dependent fixture correction #2205: draft head `bbcf1859768624c611df4abadc564c18247cf32a`. Unmerged; their source QA is not waived.
- Original contributor review docket of **15 conflicts**, **17 Article #15 / Tool #104 high-risk privacy/emergency items** and **four disputed source identities** persist. Existing R349 claims/citation registry and original Source #136/QD signoffs are not replaced.
- A real original metadata sample (`family-communication-plan.meta.json`, blob `dcad79faa8e0e6f1aef6db03e9e6e9451e19d8d3`) contains no top-level canonical URL. R350 marks absent route custody as `URL_NOT_AUTHENTICATED`, rather than claiming duplicate-URL clearance. Builder-derived canonical paths must be verified against native export before interpreting URL results.

## Conversion-first acceptance / ownership

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| One existing FV-owned Preparedness practical pack → confirmed paid order | No authenticated rights-cleared, genuinely payable SKU, delivery/refund proof | Verify merchant ownership, checkout and delivered product; make no paid CTA meanwhile | **HOLD / no merchant-confirmed order** | Founder/Commerce |
| Existing free agency-backed archive → family-contact guide → optional practical wallet card | Private Article #15/Tool #104 source, child privacy, emergency/print safety hold | Qualified claim-by-claim QD, browser/keyboard/print checks; keep Tool #102 plan builder distinct | **HARD HOLD** | Preparedness/QD |
| One authentically published Grok family-contact video → free resource landing | Matching original published asset ID, mobile route and topic not verified | Praxxis independently confirm original post/asset ID, `utm_content`, destination permissions in existing TASK-008 | **NOT VERIFIED** | Grok/Praxxis |
| Qualified visits → CTA → confirmed lead → paid purchase → net revenue | No independently evidenced paid orders, refunds/fees or attributed 7/30-day qualified-human cohorts | Audit existing measurement and merchant records without duplicate scripts | **NET REVENUE/1,000 QUALIFIED SESSIONS NOT COMPUTABLE** | Claude/Commerce |

Public candidate free destination only: https://finalvestige.com/preparedness/ . Draft, not deployed: **Start With Trusted Preparedness Resources**. Current public archive states original detailed guides are private pending review. No retired water freebie, speculative paid toolkit, invented social asset or unsupported conversion metric is introduced.

## Release decision

**OPEN / DRAFT / HARD HOLD**. No public publishing, WordPress/CMS/navigation write, analytics script, email, social post, Grok queue modification, affiliate/merchant activation, new services, spending, merge, invented QD PASS or claim of medical safety. Next steps are native authenticated 9-branch tree integration, builder-derived URL crosswalk, 100-file private build, then qualified conflict/source/claim review. Relevant coordination: #136 and #820.
