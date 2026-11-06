# R166: Preparedness Family Card offline browser QA — draft / hard hold

Issue #136; coordination #820 and charter #818. Base R165 commit: 828758fb196e4f26a2fafb7e1104a295f73ff833. This additive branch changes only a validator, tests and this review note. No changes to 35 articles, citations, source records, contributor work or WordPress.

The validator requires R165's existing immutable source and 35-article custody chain, expands the pinned quarantined Family Reunification Card JavaScript and checks the card in an offline Chromium HTML sandbox. At 360, 390, 768 and 1440 px it exercises synthetic contact input, minimal mode, four copies, print-media visibility, clearing 13 inputs, storage observations, blocked external requests and horizontal overflow. This is NOT a WordPress or real-device privacy/printing/accessibility test and cannot prove medical or emergency safety.

To run on a complete trusted checkout (Python Playwright and local Chromium required):
- python -I preparedness/tools/validate.py
- python -I preparedness/tools/build.py
- python -I -m unittest discover -s preparedness/tests -v
- python -I preparedness/tools/r166_family_browser_probe.py --repo . --report /tmp/fv-r166.json

The validator always exits 2 with DRAFT_HARD_HOLD or INVALID_HARD_HOLD; never a QD PASS.

Locally executed: 52/52 synthetic Python tests PASS, including a four-viewport Chromium fixture, an intercepted outbound fetch and print-data exposure negative case. Python compilation PASS. Native source checkout, complete build/tests, authentic R166 chained execution, WordPress browser/print tests, medical/safety/source adjudication and independent QD NOT VERIFIED (GitHub DNS failure).

Conversion-first review path, NOT LIVE: one caregiver audience topic about school pickup after evacuation -> free ungated Household Emergency Plan draft -> optional unapproved Family Reunification Card. No authenticated rights-cleared Preparedness SKU; paid offer/checkout remains OFF. TASK-008 provides no verified Preparedness Grok asset ID and campaign landing URL. No fabricated attribution, signups, paid orders, or net revenue. Highest blockers: (1) merchant rights/fulfillment/checkout proof — Commerce/Claude; (2) source/safety/QD and 35-article build — Preparedness/QA; (3) actual WordPress print/privacy QA — Site QA; (4) creator asset reconciliation — Grok/Praxxis; (5) settled orders, refunds and qualified-human sessions — Commerce/Analytics. Use #820's existing 7/30-day attribution contract; realized net per 1,000 qualified-human sessions is NOT COMPUTABLE. Retired water freebies remain retired; existing Focus Fieldbook untouched.

No production, CMS, navigation, email, affiliate, merchant, social, analytics, spending or publication action; founder release approval still required.
