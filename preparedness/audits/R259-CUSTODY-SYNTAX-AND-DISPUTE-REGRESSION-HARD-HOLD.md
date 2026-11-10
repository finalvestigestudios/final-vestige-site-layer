# R259 — R220 Python Custody Parser Repair + Actual Article #20 Dispute Regression

**Owner:** Preparedness Archive source/citation safety integration, Issue #136; conversion coordination Issue #820 and charter #818. **DRAFT / HARD HOLD — do not merge or publish without independent review.**

## Independent blocker addressed

Praxxis' source-level review of the R258 head identified a pre-existing critical Python parser defect in `preparedness/tools/r220_full_slate_draft_custody.py` at lines 127–128: JavaScript-style `//` comments were inserted ahead of R258's source-review gate constants. Python raises `SyntaxError` before R220 can audit anything. A passing isolated R258 module test cannot establish that R220 runs.

This branch changes **only those two comment prefixes** to Python `#` comments. It preserves the pinned R258 blob, the R254/R257 partition integration, all source identities, all 35 articles, all 2,000 original citation occurrences, all 32 shared-source review groups, 56 shared-source IDs, all six tools, all 41 intended WordPress draft slots, and all negative safety/commerce/publication gates.

## Independent regression gap addressed

The R258 test labeled `reclassify_article20_dispute` previously toggled an unrelated first shared-source citation row; it did not exercise the actual original Ready.gov dispute (Article #20, citation ordinal 55, source `start-ready-plan`). That meant a named mutation test could pass without testing the intended citation key.

The test now uniquely locates **(20, 55, start-ready-plan)**, asserts that the original dispute is present, changes **only its existing true dispute flag to false**, reseals the synthetic receipt, and requires the gate to reject the tampering. An additional positive control proves that this fixture contains exactly one correctly held Article #20 source occurrence.

Additional tests parse the genuine checked-out R220 and R258 Python sources using `ast.parse` without importing any production modules or executing WordPress, assert the R258 reviewer pin/call/recheck is wired, and require the review call to precede the postrender custody check.

## Scope and verification

- Two existing Preparedness-only files changed + this review-only audit record.
- R220 original Git blob `d754dbd92c9b9389de13bb3bd98395a5fec21955`; edited blob `e7566016fbc951a87add642ab4f679fef7bbec3e`.
- R258 original test Git blob `8b08f909f3b7f66d494cdd7c3bf6bd13f911a6a4`; corrected blob `4c6035f772d973c89d5743d2f97e442ac9405c65`.
- Added three new tests to R258's existing 77-method test suite; total 80 declared methods **not represented as executed unless actual Python output is captured**.
- This run's GitHub connector verified the exact upstream identities; the restricted container cannot resolve `github.com`, so full native checkout, `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, discovery of the inherited 36+ suite, 35-article source validation and 41 WordPress exports remain **NOT EXECUTED / NOT VERIFIED**. Do not confuse independent source-level/static checks with Python test execution.

## Safety, privacy and release boundaries

The source-review queue still contains 32 shared-source groups for qualified human adjudication; two original Article #7 CDC citations and one Article #20 Ready.gov citation are disputed. Article #7 chemical contamination vs microbial-treatment guidance, Article #15 and Tool #104 printable personal fields/JavaScript-disabled behavior all remain **HELD**. No medical safety, claim-support, independent QD, privacy, merchant, product-rights, checkout or release PASS.

Conversion-first task: verify an existing Grok/Praxxis TASK-008 household emergency-contact/family-record post and its asset ID/rights/mobile destination, then free Preparedness guide → optional (NOT APPROVED) Legacy Triage PDF only after full contents/rights/Access Keys privacy/checkout/delivery/fees/refunds/founder review. **No CTA deployed and no merchant-confirmed sales; net revenue per 1,000 qualified human sessions not computable.**

No changes to original articles/citations/content, source crosswalk, public site, navigation, CMS, WordPress, merchant, affiliate, analytics, email, Grok queue or spending. Review branch and tests only. See #136, #820 and #818.
