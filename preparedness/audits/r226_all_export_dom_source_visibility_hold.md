# R226 — all-export browser-semantics source and safety exposure gate (2026-11-08)

**ISSUES:** Preparedness #136; creator-to-revenue coordination #820; charter #818. **DRAFT_HARD_HOLD**. Neither this engineering work nor any locally passing unit test authorizes publication, independent QD, medical safety, or a merchant offer. No CMS, site, campaign, analytics, email, checkout or social writes.

## Exact provenance and integration

* Based **exactly** on R225 PR #1640 head `25b7996e5ec1e606ef16be9848d041517591c596` (open/draft at inspection).
* Frozen R200 manifest Git blob `5822f9dfde21d1f3bdfc26658769d852c639438c` lists 35 authored articles and six tools (41 individual WordPress draft targets; 82 WP + preview channel files).
* The seven original Claude cluster branch SHAs independently inspected via GitHub branches (2026-11-08):
  * start `2122d856fce9f64887c16df3d52e64be9f59a55b`;
  * shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`;
  * food `f911ff7a655de8d81535ea86ec3d65a49ee76648`;
  * health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`;
  * hist-field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`;
  * hist-food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`;
  * hist-home `7504a5f099594d635e3dd7332a33a2e1346c43a2`.
* Independent source/safety QA #157 draft head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, synthetic fixture #169 head `e9cd7766dac59d47ab467d8945269b9146c2aef5`, stacked fixture #973 head `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`. None imported or merged. Home Experience 2.0 lead's later draft #1626 head `c4a3c2b05c854a962ffe9645fa7a61908c1daa21`, unchanged.

## Newly covered failure modes

R220 already checked exact body-wrapper bytes, canonical route, source ordering and approximate reading depth, but these string checks did not establish how the **complete DOM** handles citation targets and disclosure visibility. R216–R218 were tightly scoped to Articles #7/#20. This new read-only R226 gate runs for **every** R220 WordPress and preview export, without editing authored texts. It:

1. Rejects duplicate document-wide IDs and duplicate HTML attributes, including browser-first `href` ambiguities.
2. Rejects `<base>` overrides, refresh redirects and unsafe anchor URL schemes.
3. Requires exact `#src-N` citation navigation and exactly one corresponding bibliography `li id="src-N"`, matched to the **article-origin selected** source URL, not a global source-ID upgrade.
4. Detects source/citation/review/body concealment via HTML `hidden`, `inert`, `aria-hidden`, and common inline CSS hiding directives, including inherited concealment; excludes script/style/template/head text from visible-warning proof.
5. Requires a visible outstanding independent source/safety/QD warning, a review record and exactly one sources section; rejects hidden bibliography links and injected source-section CSS.
6. Counts all expected source-marker occurrences and rejects missing/extra source links. No new approval state exists: valid returns only `DRAFT_HARD_HOLD`, invalid rejects to R220 `INVALID_HARD_HOLD`.

**Integration is not optional:** R220 loads the new gate from exact module Git blob `84fbbd23d3ec146221d335537fdc7a433452b5ca` using its inherited read-bound `load_frozen_gate`, then invokes it in **both channels** inside the loop over all 41 exported entries, before the post-render producer/source/original-corpus custody recheck. The bounded builder and R221/R222 pins remain inherited.

## Test and safety status (do not overstate)

* New module and regression test file were authored and **actually executed locally**, and their GitHub committed blob hashes were checked against those executable local bytes: module `84fbbd23d3ec146221d335537fdc7a433452b5ca`; tests `a21bc5fa4a8688269d18073b41342690d4b45709`.
* `python -I -m unittest discover -s .../preparedness/tests -q` against the **isolated R226 fixture**: **80/80 PASS**, including 48 parameterized HTML mutations and direct WordPress wrapper/preview/visible-warning cases. Python compilation of the isolated source/tests **PASS**. This does **not** mean the complete repository or authentic 82 channel files passed.
* R220 main-file edits were applied by GitHub contents API as five structural replacements against exact prior blob and inspected for placement. Full R220 runtime tests and the complete native `python -I preparedness/tools/validate.py` / `python -I preparedness/tools/build.py` / all-tests sequence: **NOT EXECUTED**. The local container cannot resolve github.com to obtain a trusted complete checkout (`git ls-remote` DNS failure). No authentic WordPress export inspected.
* DOM checking without actual CSS rendering, JavaScript execution or qualified visual review cannot prove real-world visibility or accessibility. Exact user-facing citation support and medical/food/CO advice still require independent source/safety reading. Do not call this `QD PASS`.

## Immutable outstanding adjudication

* Two Article #7 occurrences of `cdc-find-clean-water` and one Article #20 occurrence of `start-ready-plan` lack source-use reconciliation: **3 occurrences / 2 source IDs**.
* Seven historical shared-source-ID reading-scope collisions remain unadjudicated.
* Do not silently promote outdated source records, normalize an author's reading scope from another contributor, remove historical warning language, or downgrade a safety gate to get a green build.
* Browser DOM / WordPress editor preview and accessibility checks at 320/390/768/1440 px, hyperlink destination audits, and a human source/medical/food/CO/QD signoff remain release prerequisites.
* A previous speculative public power-outage card mismatch was **not reproduced** on current indexed Archive text: the outage card identifies FEMA; jerky references sit under validated preservation. Do not correct live content based on an unverified cache result.

## One high-intent, zero-activation commercial journey (#820 / #818)

**Audience:** households preparing an emergency contact / evacuation / document-access plan, not buyers of historical water-treatment or unsafe survival shortcuts. **Free verified present destination:** https://finalvestige.com/preparedness/ under “Create a household emergency plan” and official-agency links. Original authored long-form articles are **UNPUBLISHED / HARD HOLD**; do not link campaigns to their draft routes.

**One provisional optional product:** previously identified Payhip `Legacy Triage` ($19 reported on prior public listing), *not currently independently merchant-authenticated or demonstrably FV-owned, rights-cleared, privacy-checked, delivered, or purchased*. Do not activate a paid button or describe it as a verified FV product. A trustworthy practical download should avoid collection of passwords or sensitive account credentials and should state that it is an organizer, not official emergency advice.

**Draft CTA, disabled until product acceptance:** “Put your household's contacts and essential documents in one place. The official planning checklist above is free. An optional printable organizer may be available after our product and privacy checks are complete.” No false urgency, verified-safety implication, or claim of existing sales. Keep the urgent safety links visible and ungated.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT + PASS CRITERION | EVIDENCE NOW | OWNER |
|---|---|---|---|---|
| Existing free official household planning → Grok post | No matched published Grok `asset_id`, mobile final URL or creator rights | Cross-reference **existing** TASK-008 post+hook+actual URL, no new Grok assignment | UNVERIFIED | Grok/Praxxis |
| Free Archive → source-backed guidance | 3 citation occurrences / 7 historical collisions / no independent QD | Native validate/build, complete 82-file R226 proof, human link/reading-scope + safety check | HARD HOLD | Preparedness/independent QA |
| Free checklist → optional Legacy Triage download | Merchant ownership, privacy, PDF content and suitability unknown | Inspect rights/licensing, all file pages, exact offer language, data sensitivity, accessible mobile CTA; founder approval | NO APPROVAL | Founder/Commerce |
| Product → purchaser | No verified checkout, merchant acceptance, payment, automatic delivery, return/refund policy | Authorized end-to-end controlled order/fulfillment and refund-policy inspection; no charged test without approval | NOT TESTED | Commerce |
| Campaign attribution → net revenue | No trusted qualified-human denominator, cleared paid orders, fees/refunds or item attribution | 7/30-day `asset_id` → qualified session → CTA → confirmed lead → confirmed order/affiliate payout → fee/refund/net reconciliation, confidence flags | NOT COMPUTABLE | Analytics/Commerce |

**Metric contract:** net revenue per 1,000 qualified human sessions = 1000 × realized net attributed revenue / qualifying human sessions. Do not treat outbound clicks, tentative newsletter counts, or checkout starts as orders. Tiny sample sizes require explicit warning. No new tracking scripts or spend. Existing /focus/ lead magnet is distinct and not replaced; retired water freebies remain retired.

## Acceptance next

Use a complete trusted checkout of this exact draft head; run validate, build, complete native tests; verify all 41 source destinations and both output channels; reconcile the original 35 manuscripts against fully assembled reading depth and all source instances; triage deterministic R226 output failures without diluting the gate; submit independent qualified QD and founder release decision. Keep everything unmerged/draft and all commerce inactive.
