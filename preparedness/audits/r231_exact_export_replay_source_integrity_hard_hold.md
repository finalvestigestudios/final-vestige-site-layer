# R231 — exact replay of pinned WordPress / preview outputs (2026-11-08 PT)

**Issue:** #136. **Commercial governance:** #820, #818. **Status:** BUILT / 70 ISOLATED REGRESSION TESTS PASSED / NATIVE NOT EXECUTED / DRAFT_HARD_HOLD / NO RELEASE.

## New independent finding

R230 and earlier validators recognize many forms of malformed, hidden, or misdirected citations, but R220 could still accept extra markup outside the frozen pa-body and bibliography: a `<style>.pa-sources{display:none!important}</style>` added before a header, an extra tracking script, or an unauthorized CTA. The original body and source URLs were still present, so the existing structural checks were insufficient to authenticate *all rendered bytes*. No exploitation of public FV was observed; this is a synthetic fail-closed QA finding.

## Implementation

- `tools/r231_exact_export_replay_hold.py`: independently Git-blob-bound read-only validator. For each one of 41 article/tool entries and each of `wp` and `preview`, it invokes the already-frozen `build_article`, `wp_wrap` or `preview_wrap` in memory, compares the complete UTF-8 output byte-for-byte, and checks the five build-report fields: slug, words, minutes, source order and canonical route. A pass is only `DRAFT_HARD_HOLD`, never QD/source/medical approval.
- `tools/r220_full_slate_draft_custody.py`: pins R231 module Git blob `baf540008487ce0bad02e3b0336f1af7c045f1b4`, requires three renderer APIs from the independently pinned producer, executes R231 after R230/R226/R227 for all 82 output files, and rechecks the R231 file after the render audit. No change to frozen article-source receipts or route authorities.
- `tests/test_r231_exact_export_replay_hold.py`: 70 executed synthetic tests in local isolated environment. Test Git blob `1a5a6d5997992677f4916714346b35aa4482f6a3`, byte-for-byte compared to executed file. Two positive HOLD-only paths, five report-field mutations in each channel, and numerous adversarial full-document edits including extra CSS/JS, tracking pixels, unauthorized paid links, source-link tampering, removed reviews and altered body text.
- `tests/test_r220_full_slate_draft_custody.py`: synthetic builder fixture upgraded for exact replay, 82-invocation assertion and independent HTML-level CSS override regression. **BUILT / NOT EXECUTED in authentic repository.**

## Actually executed

`python -I -m unittest discover -s /mnt/data/r231/tests -p 'test_r231*.py'` => **70 passed**, zero errors/failures (isolated local R231 module/test only). Python compilation => PASS. GitHub-fetched R231 source and test Git identities match independently calculated local Git-blob OIDs.

**Not executed:** complete native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, inherited full discovery, 82 genuine exports, CSS rendering, links, or independent safety/QD checks. Local `git ls-remote` fails with DNS `Could not resolve host: github.com`; GitHub connector can read/write repository but cannot mount the whole repository in local test runtime. The committed R220 integration remains unexecuted and is not certified functional.

## Coordination

Original frozen contributor heads compared with **current branches: 7/7 IDENTICAL**: start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; historic-field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; historic-food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; historic-home `7504a5f099594d635e3dd7332a33a2e1346c43a2`.

Independent QA PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, synthetic-fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, follow-up #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`, and home lead PR #1674 `95d58186fde4792f05869b12f6531ff82ef4b0a0` inspected. Untouched.

Three previously flagged citation occurrences remain unresolved: #7 CDC (2) and #20 Ready.gov (1). Seven historic source-identifier conflicts remain held. No source, citation, original body, taxonomy, route, safety classification, WordPress, public website or merchant record was modified.

## Conversion-first, offer → funnel → blocker → change/experiment → evidence → owner

| Offer/funnel | Blocker | Change / acceptance | Evidence state | Owner |
|---|---|---|---|---|
| Existing Grok post → existing free /preparedness/ → official emergency-plan checklist | Actual published asset_id, post URL, rights and verified mobile destination missing | TASK-008 map real existing post/UTM, landing and editorial promise | Not verified; do not create/posts assets | Grok / Praxxis |
| Free official checklist → 35 draft originals | Original source, article safety and complete 82-export review not approved | Native build, verify source IDs, reader depth, CSS/DOM and independent QA | Hard hold; zero new original guides published | Preparedness / independent QA |
| Household documents topic → optional Legacy Triage $19 printable PDF | Vested Wisdom rights, account-access privacy, topic-fit and refund policy unreviewed | Founder/Commerce inspect complete PDF and verify seller control, terms, secure use | Public listing only; NOT approved as Preparedness upsell | Founder / Commerce |
| Paid CTA → merchant purchase and delivery | No permitted end-to-end purchase proof | Authorized checkout/refund/receipt/delivery validation | Not tested; no live CTA | Commerce |
| Asset-qualified humans → confirmed orders → net revenue | Sessions, paid orders, attribution and refunds unavailable | Join consent-appropriate 7/30d cohorts, net revenue per 1000 qualified human visits | Not computable; do not equate clicks, leads or outbound to sales | Analytics / Commerce |

Suggested **draft-only** contextual CTA on an appropriate source-verified household-documents guide: “Start with the free official household emergency-plan checklist. For organizing important family documents, a separate optional printable may be considered after product and privacy review.” **Do not show a paid-product link or publish this module** until founder/commerce and safety approvals. Disclose that a document locator tool is not an evacuation or medical safety guide, and never solicit passwords through site forms.

## Release gates remain closed

Do not merge, publish, change WordPress/CMS/nav/homepage, activate analytics/merchants/affiliates, send email, post social content, spend money or claim medical/source/QD PASS. Latest draft work is additive to seven contributor branches and independent QA; it is **not** approval to deploy.

