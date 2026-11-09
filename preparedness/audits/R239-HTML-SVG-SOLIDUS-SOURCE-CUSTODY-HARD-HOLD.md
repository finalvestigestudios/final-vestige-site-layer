# Preparedness R239 — HTML/SVG solidus source-citation custody (2026-11-09 PT)

**Source-of-truth:** #136 / #820 / #818. **DRAFT / HARD HOLD.** No WordPress, CMS, navigation, site, analytics, merchant, affiliate, email, social, spending, production release, merge or claims of independent QD approval.

## Material regression corrected

Independent Praxxis QA of R238 #1739 observed that the R238 lexer does not push **non-void** HTML elements with trailing `/>` onto its hidden-element stack. HTML browsers ignore the self-closing slash on non-void HTML tags: `<div hidden/> {{cite:ready-plan}}` remains inside the hidden div in a browser but R238 could classify the citation as visible. **R239 adds a separately frozen pre-render source gate** instead of modifying previously authenticated R238 commits.

The new Python `r239_foreign_solidus_custody_hold.py` uses quote-aware tag boundaries and explicit HTML void/foreign SVG/MathML rules. It rejects HTML `<div/>`, `<section hidden/>` and similar non-void syntax; tracks SVG `<foreignObject>` and MathML HTML integration-point descendants; fails closed on unknown self-closing foreign elements. It **preserves actual authored SVG `<rect/>` and `<path/>` diagrams**, and legal HTML void elements such as `<br/>`. It avoids interpreting `<div/>` inside comments and raw-text scripts as markup.

R220's exact-blob loader independently authenticates R239, checks 35 original bodies / 2,000 markers, requires `DRAFT_HARD_HOLD`, false publication/QD/source/medical flags and a human-review-required flag, and checks the gate blob again after auditing. Earlier R220–R238 controls remain intact.

## Evidence (carefully scoped)

- **Local isolated Python:** `python -I -m unittest discover -s preparedness/tests -p 'test_r239*.py' -v` **119/119 PASS**, `python -m py_compile` **PASS**. Test identities matched GitHub blobs: module `04b5f6e1ea20cf1039e129a155713ddac1033f82`; tests `57816a0e9ed35cb134a18c6c976d0ab4eec0feb6`. Includes 35 hidden-tag mutations + 35 SVG HTML-integration mutations + 35 valid authored-SVG controls + 14 explicit cases.
- **Authenticated GitHub corpus preflight (not the committed Python program):** read 35/35 original manuscript body blobs at R238 HEAD. A separate JavaScript lexical scan counted **733 + 702 + 565 = 2,000 original cite markers**; observed **25 actual foreign SVG self-closing tags** in two diagram-bearing originals and **no candidates** for non-void HTML selfclosing outside SVG. This is a narrow preflight, NOT native Python full-checkout execution, browser proof, or claim review.
- **Original contributor branches:** 7/7 exact GitHub refs compared to frozen R200 SHA: start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; hist-field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; hist-food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; hist-home `7504a5f099594d635e3dd7332a33a2e1346c43a2`.
- Independent QA #157 and synthetic fixture #169 remain drafts and untouched. Homepage lead #1689 untouched.
- **Blocker:** `git ls-remote https://github.com/finalvestigestudios/final-vestige-site-layer.git HEAD` fails in the Python/terminal runtime with `Could not resolve host: github.com`. Hence authentic native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, `python -I -m unittest discover -s preparedness/tests -v`, WordPress/preview exports and browser checks **NOT EXECUTED**. JavaScript read-only preflight ≠ native success.

## Source / safety adjudication HOLD

Thirty-two shared-source reading-scope groups remain human review items. Original Article #7 CDC source `cdc-find-clean-water` is disputed at two claim positions; Article #20 Ready.gov at one. Article #7's existing qualified water-review E238/E239 proposals are **not approved** and are not merged. Authored source-use notes do not prove that citations support nearby claims. No claims about potable water, medical equipment, generators, food treatment or any other advice are medically/public-health certified.

## Conversion-first, one existing offer only (no active paid link)

**High-intent topic:** household emergency contact/reunification and essential-document organization. **Free access:** https://finalvestige.com/preparedness/ official emergency resources, with no signup gate; detailed 35-article guidance remains held. **Draft on-site CTA copy:** “Make a plan your household can find. Start with our free emergency planning references.” It is text for later review, not a public change.

**One provisional optional paid candidate:** existing Legacy Triage PDF listed at $19, focused on estate/incapacity record organization. Its specific audience fit and privacy/rights are **not verified**; it is not an approved emergency-response toolkit. Draft explanatory text only after commercial clearance: “Optional paid Legacy Triage PDF: organize estate and incapacity records; this is not an emergency-response guide.” **No merchant URL activated.**

| Offer → funnel step | Blocker | Proposed change/acceptance | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Existing creator asset → free Preparedness index | Real published Grok asset ID, platform date/rights/hook and allowed UTM mobile destination missing | Reconcile actual published asset in existing TASK-008 without changing Grok's queue | UNVERIFIED | Grok / Praxxis |
| Free index → relevant long-form resource | Claim-level and 35-article build/release safety not signed | Complete native pipeline, source adjudication and independent QD | HARD HOLD | Preparedness / independent QA |
| Free guide → optional Legacy Triage | Rights, suitability, privacy, product content and founder approval lacking | Audit PDF before any merchant CTA | NOT APPROVED | Founder / Commerce |
| Optional pack → purchase/delivery | Actual merchant acceptance/checkout/fulfillment/refunds untested | Authorized merchant transaction reconciliation | NOT TESTED | Commerce |
| Qualified sessions → verified net revenue | No confirmed attributed paid orders, fees, refunds, 7/30-day sessions | Reconcile source-specific asset_id → visits → CTA → confirmed leads → paid orders → net | NOT COMPUTABLE | Analytics / Commerce |

**Net realized revenue per 1,000 qualified-human sessions: NOT COMPUTABLE, not zero.** Clicks or leads are not sales. No new offer, retired water freebie, parallel tracking script, promotion, or publisher activation.

**Next:** execute original Python validate/build/full inherited 36+ tests against an authenticated complete checkout, perform actual browser/source/citation checks and obtain independent high-consequence safety/commerce approval before proposing publication.
