# R255 — Inert, escaped source-claim review surface (Issue #136)

**DRAFT / HARD HOLD / NO MERGE OR PUBLICATION.** Stacked on R254 #1835 at exact parent `9b48661873be0ecfac79e9bb5a6f300d2831f2e1`. Read-only review integration only. Cross-reference commercial #820, charter #818, independent QA #157, synthetic fixtures #169. No changes to original 35 manuscripts, 6 tools, source register, route/taxonomy, contributor branches, safety states, editorial advice, products, checkout, or creator queue.

## Problem
R254 lets qualified reviewers inspect exact authored excerpts for all 562 citations matching 32 unresolved shared-URL source groups. Copying authored excerpts directly into HTML without correct escaping could create unintended links, executable markup or misplaced privacy disclosures. Exact URL-equality alone also fails to *flag* potential host-case/trailing-slash aliases. Neither the stored citation hash nor an apparently valid source URL demonstrates human link verification or claim/safety approval.

## New bounded safety gate
- `tools/r255_offline_source_review_surface_hold.py` authenticates R254's canonical JSON receipt, all 32 groups/56 IDs/562 workorders and the three frozen held CDC/Ready.gov occurrences. It preserves 1,438 other *unreviewed* citations, rejects duplicate source IDs, duplicate exact URLs, out-of-order citations, missing/changed excerpts, forged source/safety/QD/commercial approvals, credentials/unsafe URL characters and altered evidence checksums.
- Read-only source-link triage **flags** (does not rewrite/deduplicate/approve) non-HTTPS, IDN, IP, query and fragment references; potential hostname-case/trailing-slash URL aliases are *review questions*, not claims that two publishers or source texts are equivalent.
- Deterministic `render_offline_review` escapes authored contexts/source URL strings and shows all 562 workorders in inert, self-contained HTML. No scripts, external styles, forms, clickable links, purchased offer or affiliate insertion. Explicit `DRAFT/HARD HOLD` notice and noindex/CSP. This is an **offline human reviewer artifact, NOT a WordPress-ready public page or publication approval**. R220 only records SHA-256 and byte count in memory, writes no HTML. Optional command-line export can create a new local file, never overwrite an existing file or CMS content.
- R220 requires the exact new Git blob, invokes the guard before native WordPress renderer work and repeats source identity after audit.

## Evidence and limits
- Local isolated Python: **67/67 tests pass**, Python compilation succeeds. Adversarial changes include checksum laundering, approval changes, missing/duplicated workorders, URL injection/credentials, and HTML event handler markup in authored source context. The HTML escape test uses *synthetic* injection strings.
- Git objects of exact locally executed new validator and tests: `c53e9a6a690a826562500a88a3b1fac2597b2604`, `809a77d640faa536b7f915dd39c431d9ea585451`.
- Seven Claude original branches compared against frozen R200 manifest SHA heads; all **identical** at inspection. QA #157 `7d1ae6b8`, fixture #169 `e9cd7766`, homepage lead #1689 `f55c36b6` read-only.
- **NOT EXECUTED:** authentic R220/R255 combined receipt, full native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, inherited >36 suite, 41 real WordPress draft exports, browser and printing tests. Local `git ls-remote` fails: `Could not resolve host: github.com`. Connector can fetch individual files, but not a trusted native checkout in this environment. Gate may still surface real URL/metadata corner cases during authentic execution; keep HOLD.
- **NO** independent source approval, medical/privacy safety certification, human link-check PASS, QD PASS, public release, paid-conversion evidence, or attribution claim.

## Conversion-first P0 experiment acceptance (NOT ACTIVATED)
**One high-intent audience:** households assembling family emergency contacts and vital records. **Free destination:** existing ungated `https://finalvestige.com/preparedness/` (no new/retired water freebie). **Optional paid candidate:** already listed Legacy Triage PDF; *NOT APPROVED* as a Preparedness pack pending full contents/rights/fit/privacy and founder/Commerce merchant acceptance. Do not insert an unapproved CTA, create a new pack, or alter checkout.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Grok emergency-contact asset → free archive | Published asset_id, rights, mobile destination unverified | Praxxis/Grok verify existing TASK-008 inventory, no new creator tasks | UNVERIFIED | Grok/Praxxis |
| Free Archive → source-backed family guide/card | 32 shared-source groups/3 disputed cites plus Tool #104 privacy/no-JS discrepancy | Independent citation/claim and original browser/print review | 67 isolated tests PASS; authentic user advice HOLD | Preparedness/QA |
| Relevant free guide → optional Legacy Triage | Rights, fit, sensitive-data privacy and editorial suitability unverified | Inspect complete owned product and obtain founder commercial approval | NOT APPROVED | Founder/Commerce |
| Approved offer → paid delivery | Checkout/fees/refunds and fulfillment unverified | Authorized test of merchant order/delivery/refund | NOT TESTED | Commerce |
| Qualified creator sessions → realized net | Exact asset attribution and orders absent | 7/30-day qualified human session → confirmed order → refunds/fees reconciliation | NET REV/1K NOT COMPUTABLE | Analytics/Commerce |

Approval remains outside this branch. No production code, WordPress/CMS, navigation, analytics tags, merchant, affiliate, email, Grok queue, social posting or spending modifications.
