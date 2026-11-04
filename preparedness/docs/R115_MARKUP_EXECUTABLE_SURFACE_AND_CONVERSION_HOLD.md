# R115 — Executable-markup surface and source-token context HOLD

Scope: Preparedness Archive Issue #136 only. Business coordination #820 and charter #818. Grok/Praxxis TASK-008. Parent R114 draft PR #907 at b8eedb35b39eca10e3ca589f6bf77fe09f3f427c. Do not merge or publish.

## Purpose and engineering

The existing WordPress draft renderer performs regex substitution on raw HTML. R114 audits visible source citation counts, but token counts alone cannot rule out inline event handlers, unsafe URL protocols, executable styles, interactive-element citation abuse, nested links, embedded content, or forged publication/review-state changes. R115 adds a separate independent read-only HTML surface audit over all 35 original authored article drafts, with a fixed expected roster and comparison to the independent R114 source-scope report. It reports deterministic category flags and body fingerprints instead of raw source URLs, claim prose or false factual/medical clearance.

Read-only command: python -I preparedness/tools/r115_markup_executable_surface_gate.py --repo-root .
Exit zero means a HOLD report was generated, NOT that content passed qualified review or may be published. Exit two means integrity or loading failed closed. Any flags require human adjudication; conservative flags must not be silently removed or treated as source support proof.

Synthetic tests: python -I -m unittest discover -s preparedness/tests -p 'test_r115_*.py' -v
Isolated local scratch exercise: 80 adversarial/unit tests passed (62 markup mutations, 10 metadata-state mutations, 8 core). Committed tests use correct repository-relative import; exact-head GitHub runner testing, native validation, offline WordPress build, full Python suite, and actual 35-article scan are NOT YET VERIFIED. The private workflow requests all those steps without weakening the mandatory release pipeline.

## Latest reviewed exact contributor references

- Start Here: claude/prep-start-bbfeb8 = 2122d856fce9f64887c16df3d52e64be9f59a55b
- Shelter follow-up: claude/prep-shelter-followup-evidence = 6a5998ead97eca997e573ce8d3ceacf1c6aabad4
- Food: claude/prep-food-ccdc55 = f911ff7a655de8d81535ea86ec3d65a49ee76648
- Health: claude/prep-health-837444 = d5ef5bafd68361434dd1cc9209915b8e8a4eaf17
- Historic food: claude/prep-hist-food-b81f19 = 67e116e536c7410bed30f8f3b1bb8c166f3c223d
- Historic home: claude/prep-hist-home-0e0e38 = 7504a5f099594d635e3dd7332a33a2e1346c43a2
- Historic field: claude/prep-hist-field-9db767 = 4e5caf812727953aa45e3bda2d382f2c67b6a09c

Separate release candidate PR #584 ddb3528ba6494dada1fa1c3a142ce746e3a67706 (draft HOLD). Independent QD PR #157 7d1ae6b8ef93d10cfb6810987672360885e9c1aa (draft), synthetic fixture PR #169 e9cd7766dac59d47ab467d8945269b9146c2aef5 (draft), homepage #49 10495883299d53596992c26a8987f629b2904670 and flagship #604 bdf01b4a3e13fd6179ae9e847c9d4429bbe16176 inspected but untouched. PR #169 fixes the first _upgrade_test.json fixture race yet still writes _dup_test.json to the shared source tree in test_register_fragments_cannot_duplicate_ids. That test needs an isolated temporary copy before merge.

## Conversion-first handoff — offer → funnel → blocker → experiment → evidence → owner

| Priority / Offer | Funnel step and blocker | Safe next experiment / acceptance | Evidence | Owner |
| --- | --- | --- | --- | --- |
| P0 / genuinely purchasable FV-owned Preparedness pack | Paid checkout and usable delivery. No authenticated merchant/rights-cleared Preparedness SKU proven. | Review existing seller listing, product ID, rights, content, price, download, refunds, fees and accepted seller fulfillment; no paid CTA before proof. | UNVERIFIED, not zero sales. | Growth / Claude / founder |
| P0 / authentic free household emergency plan | Reader trust. Original source scopes, 23 contributor changes, 30 shared URLs, 15 safety exceptions, 22 editorial decisions and qualified review pending. | Reproduce R111 lineage and collision worklist, R114 citations, R115 markup, human source check, independent qualified emergency advice and QD review. | 80 local synthetic R115 tests only; no source/medical approval. | Preparedness / independent QA |
| P1 / Grok matching household planning video | Social asset to free guide. No verified matching TASK-008 asset ID, post URL, destination or production route. | Grok supplies immutable asset_id; Praxxis checks topic and links; Claude stage-tests caption/bio mapping, 360/390/768/1440px, browser/print and accessible controls. | NOT OBSERVED qualified sessions. | Grok / Praxxis / Claude |
| P1 / optional matching commercial pack | Guide to voluntary paid CTA, merchant checkout and download. No approved SKU or deliverable. | Stage only after product approval; contextual label/disclosure/price; checkout consent, receipt, refund, file delivery and mobile/keyboard acceptance. | NOT TESTED; no claimed sales. | Claude / Site QA / founder |
| P1 / verified revenue cohort | Asset ID to approved qualified human session to relevant CTA to merchant-paid order less fees/refunds. No reconciled records. | Privacy-safe 7/30d small-N scorecard using existing instrumentation and seller exports; no duplicated analytics scripts. | N/A net revenue per 1000 sessions, not invented zero. | Growth / Claude / Praxxis |

One proposed free guide: household-emergency-plan at /preparedness/start-here/household-emergency-plan/ — NOT LIVE VERIFIED, still pending safety. The original author-source bibliography must remain intact. Never paywall emergency guidance. Do not revive retired water downloads, create new unapproved products or alter the current Focus Fieldbook. Grok owns videos and posting; Praxxis independently reviews TASK-008; Claude owns production engineering; founder approves releases and costs.

Campaign landing checks: real approved Grok asset_id, correctly attributed link or bio-route with UTMs, editorially matched free guide accessible on mobile without signup, visible sources and warnings in mobile/print, optional verified paid pack with transparent terms, functional staged checkout, merchant-confirmed accepted order, receipt/file delivery, fees/refunds and verified net revenue. Links, clicks, signups and checkout starts are not paid sales.

Release status HOLD. No merge, production site, CMS, nav, tracking, social, email, seller or public changes. No QD PASS, no medical or factual clearance.
