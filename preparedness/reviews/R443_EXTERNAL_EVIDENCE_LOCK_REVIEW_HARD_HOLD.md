# R443 — externally pinned original-source evidence lock (DRAFT / HARD HOLD)

**2026-11-17 PT · Issue #136 · conversion #820 / charter #818**  
**Parent:** R442 draft PR #2905 at `5d4d24555ec79c1bd39e00a1d3d033aa550d4127`.  
**Scope:** additive Preparedness-only source/citation and original-manuscript custody; **no publication authority**.

## Concrete defect guarded

R442 requires an "independent frozen citation baseline," but source matching alone cannot establish that the baseline was independently pinned: if someone edits the body, source annotations, and baseline together, a self-consistent but silently rewritten evidence package can pass its internal equality checks. R443 requires an **externally supplied exact SHA-256 lock pin** whose independently reviewed origin must be checked separately. Per-article lock rows join original Git blob identity + raw bytes SHA-256 + exact byte length + full canonical per-article citation-annotation hash. The lock covers the entire R397 original docket, full R442 annotation object, and all nine current branch heads. It composes R440 original docket/source/fork checks and R442 citation-to-claim/variant/reading-scope checks.

The pin is **integrity, not authorization**: an operator could still independently forge a new pin. R443 never claims to verify signer/reviewer identity and always returns `DRAFT_HARD_HOLD` / exit 2. Actual independent source adjudication, qualified emergency/food/medical/privacy review, complete native build, browser validation, merchant and founder approval remain hard blockers.

## Verification

- **Actual observed GitHub contributor heads checked this run**: `claude/prep-start-bbfeb8=2122d856fce9f64887c16df3d52e64be9f59a55b`; `food=f911ff7a655de8d81535ea86ec3d65a49ee76648`; `health=d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; `hist-field=4e5caf812727953aa45e3bda2d382f2c67b6a09c`; `hist-food=67e116e536c7410bed30f8f3b1bb8c166f3c223d`; `hist-home=7504a5f099594d635e3dd7332a33a2e1346c43a2`; `shelter=5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; `shelter-continuation=ac8625faf30dd5538fadc31e06cb5a2cea1defae`; `shelter-followup=6a5998ead97eca997e573ce8d3ceacf1c6aabad4`. All nine matched the **actual original R397 docket** Git blob `86d22a1d504c93db7689b914e2202a7845b648e2`. Self-ref compare 0 ahead, 0 behind. No branch written to.
- Original docket still records 35 manuscripts, 203 original source IDs, 280 source-record occurrences, 181 distinct URLs, 17 shared URL review groups, five unresolved source disputes and nine unselected forks. None adjudicated, deduplicated away, or promoted.
- Independent QA #157 exact head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` and synthetic fixture #169 exact head `e9cd7766dac59d47ab467d8945269b9146c2aef5` remain open drafts, unmerged. Fixture-dependent #2205 head `bbcf1859768624c611df4abadc564c18247cf32a`; homepage #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0`; editorial #2789 `93855eb1227f7efe0d295eb495cd05f95216b86d` inspected without change.
- `python -I -m unittest discover -s preparedness/tests -p 'test_r443*.py' -v`: **86/86 PASS**, synthetic only.
- `python -I -m unittest discover -s preparedness/tests -p 'test_r44*.py' -v`: **229/229 PASS**, local R440, R442, R443 subset.
- `python -m compileall -q`: **PASS** on focused modules.
- Both new tool and tests Git blob identities matched exactly the locally executed code: tool `e5a5494ada17c589447ce8474651cd3f9f849adb`, tests `b07da0ea02b06a6fcd75686a3544b86c745545bd`.
- **Not a cumulative PASS**: a broad assembly of historical R433–R443 ZIPs was attempted and failed (495 tests, 43 failures, 5 import/setup errors), owing to incomplete/uneven inherited module packaging and missing R434/R436/R441 restored parent files. Do not misreport 927 cumulative tests passing. Historic R442 841/841 was a prior-turn local report, not reproduced this run.

## Still hard held

The original 35 manuscripts plus independently frozen claim annotations and externally authorized evidence lock are **not provided as one trusted checkout**; 70 actual WP/private-preview exports and CSS captures, native `validate.py`/`build.py`, no-JS/print browser checks and qualified QD remain **NOT EXECUTED / NOT APPROVED**. A CLI structural error or synthesized clean fixture does not imply article-safety approval.

## One conversion-first research lane (no activation)

**Audience:** existing already-published and rights-cleared Grok family-contact/reunification clip, if one can be authenticated. **Free guide:** the existing public official-source `https://finalvestige.com/preparedness/`. **Draft CTA only:** "Review the official household emergency checklist." **Optional practical tool:** Tool #104 family contact wallet card remains draft, separate from Tool #102, with emergency guidance and child-privacy/print approvals missing. **Paid option:** no verified existing FV-owned, rights-cleared, actually payable and deliverable Preparedness pack/SKU or merchant refund and settlement evidence. Never use the retired water freebies or unrelated Vested Wisdom merchant listing.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / ACCEPTANCE | RESULT | OWNER |
|---|---|---|---|---|
| Existing FV Preparedness pack → verified paid order | No authentic SKU/license/checkout/delivery/refunds | Verify through owner and merchant independently before adding any paid CTA | HOLD | Founder/Commerce |
| Genuine Grok family-contact asset → free agency-backed Archive | No matched immutable asset_id + post URL/rights/date/hook/mobile URL | Praxxis independent source/post QA; Grok retains creator/post role | UNMATCHED | Praxxis/Grok |
| Free guide → optional Tool #104 download | Article #15 accuracy, Tool #102/#104 identity, child privacy, no-JS/print QA | Qualified source, privacy and accessibility signoff before any link | HOLD | Preparedness/QD |
| Qualified human landing → CTA → confirmed lead → paid order → refunds/fees → net revenue | No asset-level session proof, no merchant-paid conversion or fee/refund data | First-party consent-aware 7/30-day cohort spec with Claude; do not add scripts | NOT COMPUTABLE | Claude/Commerce |

No claimed traffic, leads, sales, net revenue, subscription confirmations, or conversion improvement. No CMS, navigation, social queue/post, email, analytics, merchant activation or spending changes. Founder retains release authority.
