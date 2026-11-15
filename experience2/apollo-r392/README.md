# Apollo Experience 2.0 / R392 — semantic source custody gate

**REVIEW ONLY — NO MERGE OR DEPLOYMENT.** This source-controlled QA improvement stacks on draft R391, isolated from frozen homepage PR #49, Research Desk PR #158, and Grok/Praxxis TASK-008.

## Reproduced gap and solution

R391 counted six evidence cards, two NASA publisher links, and one free CTA; those numerical checks could pass with materially falsified claims or changed destinations. R392 adds exact source-content acceptance from the existing, sealed Apollo R377 six-record research ledger (SHA-256: 60bfa330398b7684463c95afcc7e6ef347d44f22d5a2f1350286a660edb3a76f). It checks the six claim/boundary/source-role/photo-limit texts, chronological sections, source destinations, original report vs retrospective classification, deep links, disclosure, non-endorsement rights text, and one noncommercial CTA. It rejects duplicate IDs and unreviewed imagery. No tracking, WordPress writes, added front-end JS, paid services, or invented Atlas geography.

The existing inherited staging_smoke.py now executes this semantic check on both JS-enabled and JS-disabled browser sessions, preserving the R391 read-only same-origin network restrictions, CSS digest check, genuine axe-core prerequisite, and screenshot/performance instrumentation. The new qa/test_semantic_custody.py is a real Chromium local-fixture regression that exercises 320–1920px, keyboard/touch/native details, no-JS, forced colors, reduced motion, large-font stress and ten adversarial falsification cases.

## Sources, rights and chronological caution

- Original Board report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
- NASA retrospective (February 14, 2018): https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/
- NASA media rights/non-endorsement: https://www.nasa.gov/nasa-brand-center/images-and-media/

Six questions are supported by two publications, not six independent documents. The 102 deliberate Command Module test ignitions occurred December 1967–February 1968, after the January 1967 fatal fire. The Board did not conclusively identify a particular ignition source. No NASA photos or logos added. This is not new rights clearance.

## Local testing and staging command

In a full checkout, use inherited R389 qa/contract.php to generate experience2/apollo-r392/QA/local-php-fixture.html (untracked fixture), then run:

    python experience2/apollo-r392/qa/test_semantic_custody.py

Only after explicit staging authorization and independently pinned genuine axe-core run:

    python experience2/apollo-r389/qa/staging_smoke.py --url https://APPROVED-STAGE/apollo/ --approved-staging-host APPROVED-STAGE --axe-script /reviewed/axe.min.js --axe-sha256 REVIEWED_SHA256 --output-dir /tmp/apollo-stage

The inherited harness blocks production origins and mutating requests. A local fixture pass does not establish installed WordPress/Assembler, actual HTTPS/CSP, genuine axe, independent screen readers, field CWV or exact-HEAD hosted CI. All remain HARD HOLD with QD/founder approval required.

## Revenue-first pathway

Grok-approved Apollo long-form film (real asset_id and approved organic UTMs) → source-verifiable gallery → one free Apollo investigation CTA → separately approved educator kit once rights-cleared product, merchant checkout and delivery are proven. Commercial conversion is not observed. Count qualified-human sessions, CTA, confirmed lead, merchant-confirmed paid orders, refunds/fees and realized net revenue separately; net per 1,000 qualified sessions and 7/30-day cohorts are unavailable. Owner: Grok/Praxxis acquisition; Apollo QA site evidence; Claude production commerce/analytics; Founder release. Cross-reference #150, #820 and charter #818.
