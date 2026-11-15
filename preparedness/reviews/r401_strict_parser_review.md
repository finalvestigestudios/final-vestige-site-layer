# R401 — Article #11 strict source-evidence parser (DRAFT / HARD HOLD)

Scope: Preparedness Archive source/citation custody only, [Issue #136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Stacked on [R400 #2672](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2672) at its inspected HEAD `c1d111c3799ca416e4856d82d8586fcb6aa6d27d`. This PR is **not qualified food-safety review**.

## Demonstrated integrity defect and bounded change

The existing R400 checker accepted extra JSON attributes at registry/source/conflict levels and repeated review requirements as a structural `PASS`, even when the extra attribute contained an unreviewed household storage instruction. Passing an incorrectly typed nested `expected` field also raised an unhandled `AttributeError`, rather than returning a structured fail-closed receipt. Neither defect granted publication: R400's release status already remained `DRAFT_HARD_HOLD`.

R401 preserves the pinned original 35-article/203-source-ID/280-occurrence source docket, the five disputed original source scopes, nine unselected Shelter forks, R400 five source scopes and four scope collisions. It changes only the R400 validator and adds an isolated synthetic regression test. The additional read-only ingress checks:

- Duplicate JSON keys and non-finite constants are rejected, without last-wins semantics.
- Unknown or missing registry/source/conflict fields cannot smuggle unreviewed instructions or fictitious reviewer decisions.
- Repeated or malformed mandatory qualified review requirements are rejected.
- Non-object or structurally corrupted nested records cannot crash the inspection API; they receive a structured `FAIL` with `eligible=false`.
- Inputs are bounded to 2 MB each. Missing original evidence, invalid SHA and impossible release flags remain rejected.
- Even **structurally valid evidence is never eligible** and CLI must return exit 2 `DRAFT_HARD_HOLD` until independent source, food-safety, privacy and editorial approvals.

Local evidence (2026-11-15 PT): baseline R400 accepted three manipulated inputs as structural `PASS` and raised `AttributeError` on a fourth. Patched exact-code local suite: 166 unittest cases PASS (original R400 97 + new R401 69), Python compilation PASS. R401 validator Git blob `85b1cddb6818b38fc13355628b2d011fac851b95`; test Git blob `ca28ec6b62a1bafb5a7174a9a15f2307e12abdc3` matched locally exercised bytes. Full original native validate/build and actual WordPress/preview exports **NOT RUN** (no authenticated full checkout in local environment). GitHub Actions cannot be counted as PASS. Human food safety/QD **NOT APPROVED**.

### Qualified reviewer checklist (unresolved)

1. Inspect the complete Article #11 manuscript and every claim/citation position against primary NCHFP and current USDA/extension food-safety context. Resolve University of Minnesota institutional audience/product-scope tension, conditional homemade-method scope, archived 2011 FSIS versus newer full-text FAQ before offering advice.
2. Independently adjudicate five source-reading disputes and nine Shelter source/manuscript forks without auto-selection, URL collision, shortened reading depth or evidence loss.
3. Re-execute native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py` and `python -I -m unittest discover -s preparedness/tests -v` against authenticated full checkout, plus private frozen export comparison; inspect independent draft QA #157, fixture #169 and dependent #2205.
4. Obtain human-reviewed source/food/medical/privacy/accessibility approval independently of machine structure, then founder release approval; keep production/CMS/nav/social/commerce untouched meanwhile.

## Conversion-first friction contract (NO paid activation)

| OFFER → FUNNEL STEP | BLOCKER → CHANGE / EXPERIMENT | EVIDENCE | OWNER |
|---|---|---|---|
| One *existing* licensed FV Preparedness digital pack → merchant checkout → usable delivery | No authenticated FV-owned, payable, rights-cleared, deliverable SKU; verify listing, true seller, fulfillment, fees, refund policy, accessibility and receipt | **UNVERIFIED; paid CTA HARD HOLD** | Founder / Commerce |
| ONE authentic already published family-contact/reunification Grok asset → existing free agency-backed Archive | No independently matched `asset_id`, actual URL, hook, link rights or signed-out/mobile topic-parity result; verify before any CTA or UTM | **UNVERIFIED; no campaign claimed** | Grok / Praxxis |
| Free `/preparedness/` guide → optional Tool #104 | Original Article #15, family-contact printable, child privacy, school protocol and accessible printing not cleared | **HARD HOLD; free-only CTA unpublished** | Preparedness / QD |
| Qualified human `utm_content=asset_id` session → relevant CTA → actual confirmed lead → merchant-settled paid order → net proceeds | Consent/attribution, verified orders, fees/refunds and 7/30-day cohorts absent | **Net revenue / 1,000 qualified sessions NOT COMPUTABLE** | Claude analytics / Commerce |

Public agency emergency resources remain free. Draft-only free CTA: **Start With Trusted Preparedness Resources** → https://finalvestige.com/preparedness/. No retired water freebies, invented products, unrelated Grok assets, tracking script, social posts, emails, CMS writes, navigation changes, merge or deployment. Founder retains paid/release approval.

**Release: DRAFT / HARD HOLD. Machine integrity PASS is not medical/food/emergency safety or QD PASS.**
