# R310 — six Preparedness tools: identity, citation, and no-JavaScript safety gate

2026-11-11 PT / 2026-11-12 UTC | Issue #136 | Commercial coordination #820 | DRAFT / HARD HOLD.

## Authenticated findings from R309 branch at 539dd87d8202646cf6f794dc836e01bb59c30255

The six source tool body and metadata pairs (12 Git blobs) exist. Each tool's distinct citation IDs in the body exactly match its own metadata source_use IDs. This is identifier parity, not proof of source accuracy, human source review, medical safety or a complete WordPress render.

| Exact source slug | Contributor n | Citation IDs | noscript occurrences | Review |
| --- | ---: | ---: | ---: | --- |
| water-planner | 101 | 3 | 0 | pending |
| home-fire-escape-worksheet | 102 | 7 | 1 | pending |
| reunification-plan | 102 | 7 | 1 | pending |
| kit-builder | 103 | 22 | 0 | pending |
| power-outage-planner | 103 | 17 | 1 | pending |
| family-reunification-card | 104 | 11 | 3 | pending |

New integration conflict: 102 and 103 each identify two distinct tools. These may be contributor-local numbering rather than a global SKU; do not use "#102" or "#103" alone as an authority to merge, rename, route, bill for or publish a tool. R310 flags duplicates until editorial numbering authority is resolved. Both kit-builder and water-planner contain scripts but lack an explicit noscript fallback witness in their source. They require real browser, print and disabled-JS QA; missing markup is an acceptance gap, not independently proved inaccessibility.

## New read-only code

- preparedness/tools/r310_six_tool_identity_citation_privacy_hold.py pins all 12 source blobs, exact R309 predecessor, and taxonomy; rejects missing/added source pairs, symlinks, changed source bytes, wrong identities/unsafe review status, mismatched source_use/citation sets, unknown internal destinations, duplicate numbers and static network/storage/remote-script patterns. JavaScript-dependent HTML lacking a noscript witness is blocked pending review.
- preparedness/tests/test_r310_six_tool_integrity.py executes 97 isolated synthetic tests, including all six tools, duplicate-number source observations, fabricated safety PASS, network/storage mutations, citation mismatches, unapproved publication, and no-JS controls.
- Local Python compilation PASS; 97/97 local synthetic unit tests PASS against the GitHub-identical file bytes; deliberately incomplete native checkout rejected with INVALID_HARD_HOLD exit 1.
- Complete authenticated native validation/build, all 41 genuine WordPress drafts, live merchant/affiliate claims, static-to-browser privacy equivalence, print/no-JS responsiveness and independent QD/safety approval NOT EXECUTED / NOT VERIFIED.

PR #157 remains an independent draft safety repair. PR #169 remains an independent draft with a source-directory fixture write in its _dup_test test, even though the inspected integrated R309 test itself uses an isolated temporary copy. Home lead PR #1689 unchanged. All seven canonical Claude branch heads freshly compare identical to the frozen R200 references; separate Shelter descendants remain under reconciliation. Ten substantive body differences and twelve metadata revisions remain under hold.

## Conversion-first acceptance — one intended audience, not an approved offer

| OFFER -> FUNNEL STEP | BLOCKER -> CHANGE | PASS/FAIL EVIDENCE; OWNER |
| --- | --- | --- |
| Authenticated existing Grok family-contact topic -> free official preparedness resources | Verify a genuinely published matching asset_id and permitted mobile destination through existing TASK-008, no queue overwrite | NOT VERIFIED; Grok/Praxxis |
| Free source-backed family plan guide -> optional free family-reunification-card | Retain original distinct tool source, complete child privacy/emergency-message review and native print/no-JS/browser QA | HARD HOLD; Preparedness/QD |
| Free guide -> optional one owned paid practical pack | No independently verified FV rights-cleared, currently purchasable, deliverable audience-matched Preparedness SKU; owner to verify merchant rights, checkout, fulfillment, refunds | NO APPROVED OFFER; Founder/Commerce |
| Qualified-human visits -> confirmed leads/paid purchases -> net revenue | No merchant-confirmed attributed orders/fees/refunds or qualified cohort denominator; use 7/30-day measurements only after consent-respecting verification | NOT COMPUTABLE; Claude/Commerce |

Draft free-only copy for review: "Make a plan for how your household will reconnect. Start with free official preparedness resources." The existing free-resource destination candidate is https://finalvestige.com/preparedness/ . Nothing in this audit is a paid-CTA or a live publishing decision.

Release controls remain DRAFT / HARD HOLD: no merges, WordPress/CMS/navigation changes, merchant/affiliate activation, social posts, emails, analytics scripts, production release, new sales claims or spending.
