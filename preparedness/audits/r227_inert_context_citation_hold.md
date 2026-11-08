# R227 — fail-closed inert/conditional citation exposure (2026-11-08)

**Issue #136; commercial coordination #820; charter #818.** DRAFT / HARD HOLD. This is integration/source-citation safety engineering only, **not independent QD, medical/food/CO guidance approval, WordPress publication, a release approval or a revenue claim**. Branch derived exactly from R226 PR #1646 at `6e09f0944e490587b9df4b0d47ae20db8538f7e6`.

## Source of the defect and bounded correction

R226 checks duplicate IDs/attributes, link destinations and inline hidden states, but HTMLParser reports elements inside `<template>` and `<noscript>` as parseable tags even when they are not displayed in a normal browser reading surface. The R226 warning collector specifically ignores `template` but does not exclude `noscript`. Closed `<details>` and `<dialog>` can likewise conceal the sources, review record or safety warnings. Browser repair of misnested HTML may also relocate/reparent critical markup. Therefore presence of the right IDs/URLs in source markup alone does not establish visible safety disclosure.

**R227 adds a separately pinned, read-only companion gate** `tools/r227_inert_context_citation_hold.py`, exact Git blob `0a15ea6fdfe60009d97fbbe4340aa5b03d111285`. It rejects article body, citation elements, bibliography entries, and review record within inert/conditional HTML containers (template, noscript, script/style/head, iframe/object/canvas/svg/math/select/textarea/audio/video, closed details/dialog), refuses pending-review warnings whose only readable copy is in these contexts, and detects unclosed/misnested critical elements. Open details/dialog and unrelated inert fragments are allowed. Only successful state: `DRAFT_HARD_HOLD`; release_authorized is always false.

The existing R220 custody loop loads R227 from **the exact authenticated Git bytes** and runs it immediately after R226 for each of 41 entries in both WordPress and preview channels (82 intended files). It does not replace the per-article source-URL/ordinal, content-depth, canonical-route, taxonomy, producer-bundle, and source crosswalk checks inherited from R214–R226.

## Evidence actually obtained

* R227 module Git blob matches the exact locally executed source: `0a15ea6fdfe60009d97fbbe4340aa5b03d111285`.
* Regression test file Git blob matches the exact locally executed tests: `f6af9cab7a207127f7b343e6f6da0328523073b5`.
* `python -I -m unittest discover -s /mnt/data/preparedness_r227 -p 'test_*.py' -v`: **68/68 PASS**, including 48 specific role × inert-context negative mutations; isolated synthetic baseline, WordPress HTML block, HTML preview, open-details/dialog positives, conditional warning and malformed-close negatives.
* `python -m py_compile` for both exact locally executed files: **PASS**.
* R220 integration edit: five unique, anchored replacements at the exact retrieved parent blob, now requiring R227 HOLD in the full 41 × 2 render loop; GitHub commit confirms new code. **Not executed against the complete authentic source repo.**
* Seven contributor branch heads independently resolved and matched R226 receipts: start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; historical field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; historical food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; historical home `7504a5f099594d635e3dd7332a33a2e1346c43a2`. Independent QA #157 at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; food fixture #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5` and successor #973 at `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`: inspected, left unmerged.

## Blocking release gates, unchanged

* Full repository checkout remains blocked in this environment: `socket.gethostbyname('github.com')` -> `gaierror(-3, 'Temporary failure in name resolution')`. Therefore **native** `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, full `python -I -m unittest discover -s preparedness/tests -v`, and actual 35-manuscript / six-tool / 41-export / 82-channel R227 validation are **NOT EXECUTED**.
* Three unresolved citation occurrences: two Article #7 CDC instances (`cdc-find-clean-water`) and one Article #20 Ready.gov instance (`start-ready-plan`). Seven historical source-ID collision scopes require independent original-reading adjudication. No automatic source substitutions or safety-state promotions.
* R227's HTMLParser is **not an HTML5 browser, CSS computed-style renderer, JS runtime, or accessibility auditor**. Actual WordPress DOM/source click and independent qualified human medical/food/CO/source QD remain required. These tests prove neither safety nor commercial success.

## Founder commercial priority — ONE provisional route, activation = zero

**High-intent audience:** households organizing emergency contacts, essential documents and family evacuation/reunification plans. **Currently published free destination:** https://finalvestige.com/preparedness/ (official-agency family emergency planning section); the 35 new long-form drafts are **NOT published**. **Provisional optional merchant item:** Legacy Triage, prior public $19 Payhip listing; NOT verified merchant-owned, FV rights-cleared, complete-file privacy-reviewed, checkout-accepted, fulfilled or purchased. Do not present it as approved/currently integrated.

**Draft CTA, disabled**: “Plan your household's emergency contacts and documents with the free official resources above. An optional printable organizer will be offered only after its contents, privacy and checkout are independently verified.” Keep all urgent safety material free and ungated; no retired water freebies, new product creation, unapproved merchant URLs or forced upsells.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT & PASS EVIDENCE REQUIRED | OWNER |
|---|---|---|---|
| Existing Grok asset → free family emergency guidance | No confirmed post `asset_id`, exact hook, rights, mobile final URL | Match **already-published** creator record from TASK-008 and use existing allowable UTM only, no queue changes. Current: UNVERIFIED | Grok / Praxxis |
| Public free guide → source-backed detail | Three citation occurrences, seven crosswalk conflicts, authentic build/QD missing | Complete native validation, click/citation/source/medical review; current: HARD HOLD | Preparedness / independent QA |
| Free planning → optional Legacy Triage | Rights, file privacy, use-case and commercial approval unverified | Inspect full PDF, seller identity, accessible truthful optional CTA, founder signoff; current: NOT APPROVED | Founder / Commerce |
| Optional product → paid order | Checkout, delivery, refund and privacy handling not verified | Founder-approved controlled merchant transaction and delivery/refund inspection; current: NOT TESTED | Commerce |
| 7/30-day asset-attributed human visits → net realized revenue | No trusted denominator, confirmed orders, fees/refunds or platform ledger | Per-asset qualified session → CTA → confirmed lead if any → provider-paid order → refunds/fees → realized net. Current: NOT COMPUTABLE | Analytics / Commerce |

Net revenue per 1,000 qualified human sessions is intentionally **not computable** until both numerator and denominator are verified. Neither a click, email subscription nor checkout start is revenue. No new scripts, campaigns, purchase attempts, CMS, social, affiliate, navigation, email or spending changes in R227. All publishing/release approvals remain with the founder.
