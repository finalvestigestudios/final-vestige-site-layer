# R228 Preparedness source-link descendant visibility — 2026-11-08 PT

**Governance:** Issue #136; cross-reference #820 / #818. **DRAFT_HARD_HOLD; no QD PASS or publication authority.** This is a scoped, isolated follow-up to draft #1653 / R227, at exact parent commit `96db7f317b2bbd153c0f3db49dded9df27ebfd1c`. No original article, metadata, taxonomy, source register/crosswalk, canonical URL, WordPress export or commerce integration modified.

## Independent failure mode repaired

Independent Praxxis/Grok handoff review identified two actionable issues with R227. First, `preparedness/tests/test_r227_inert_context_citation_hold.py` resolved the protected module using `with_name(...)` beside the test even though it lives in `preparedness/tools`. The import path is corrected to the repository's actual layout.

Second, the prior guard rejected `<template><li id="src-1">...</li></template>` but did not reject **inert descendants** of an otherwise visible source entry, such as `<li id="src-1"><template><a href="https://...">source</a></template></li>`. R226's permissive HTMLParser can still see that URL and count the target. R228 rejects conditional/inert descendants inside `pa-sources`, `pa-cite`, `pa-review`, including closed `details`/`dialog`; and a source-fragment anchor concealed within body markup. Unrelated decorative body templates, open details/dialog, ordinary WordPress wrapper and preview wrapper remain acceptable. R220's exact R227 module-blob pin was updated, retaining the original integrated 41 × two-channel gate rather than introducing a disconnected pass.

## Exact custody

- Source `preparedness/tools/r227_inert_context_citation_hold.py`: Git blob `dd9f3fc97fb9a92231f7f882cacb021d1d115d12`.
- `preparedness/tools/r220_full_slate_draft_custody.py` pins **that** R227 blob. It does not change the approved identity of any article/source.
- Existing R227 regression's module path corrected; new R228 16 inert tags × 3 semantic roles = 48 negative mutations + 10 explicit edge/positive scenarios.
- Seven original Claude heads (GitHub compare each to itself, 2026-11-08 PT): start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; historical-field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; historical-food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; historical-home `7504a5f099594d635e3dd7332a33a2e1346c43a2`. No branch changes made.

## Executed verification and hard limits

- **126/126 Python `unittest` checks PASS** in an *isolated mirrored tools/tests layout*: 68 inherited reconstructed R227 cases + 58 new R228 cases; Python syntax compilation PASS. The mirror exercises equivalent R228 guard logic and the corrected repository-relative import pattern. **Do not represent this as execution of exact GitHub-committed source bytes.**
- The committed R228 test file was added for eventual **native** discovery. Complete trusted checkout, `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, and full repository `python -I -m unittest discover -s preparedness/tests -v` were **NOT EXECUTED**. Container `socket.getaddrinfo('github.com',443)` failed with `gaierror [Errno -3] Temporary failure in name resolution`.
- **82 authentic WordPress/preview renders NOT INSPECTED.** Prior synthetic-only results are not real exports; no independent browser/CSS accessibility proof.
- Independent QA PR #157, synthetic-fixture #169/#973 and homepage #1652 were inspected, not merged. Original Article #7 two CDC occurrences, Article #20 one Ready.gov occurrence, and seven historical source-ID reading-scope conflicts remain **HARD HOLD**; source, medical/food/CO and QD reviews remain outstanding. Editorial E227 Article #20 proposal is separate and not silently imported.

## Single-offer conversion acceptance: NOT APPROVED

Audience/topic: families organizing **first-contact information, family documents and evacuation communication**. Already-live no-gate source-backed destination: https://finalvestige.com/preparedness/ → *Create a household emergency plan* → FEMA/Ready.gov official planning checklist. The 35 authored long guides are not live. The one provisional practical-product candidate is **Legacy Triage**, https://payhip.com/b/n1RhV , advertised at $19 as a 580KB printable PDF under the **Vested Wisdom** seller name. It is oriented to incapacity/estate document continuity and account access, not direct evacuation action. This is a **weak-fit, potentially sensitive** upsell, not a rights-cleared FV preparedness product. Storefront display is not proof of seller authority, successful checkout, delivery, customer consent, order, refunds or net revenue.

**Draft-only CTA concept, not to be shipped:** “Start with the free household emergency-planning checklist. Keep local emergency contacts and document locations handy.” No paid CTA until exact product rights, safe password/storage instructions, accurate disclosures, checkout and fulfillment are independently verified. Do not use retired water freebies.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Grok published asset → official planning free destination | Creator asset_id, exact social post, hook, rights, mobile UTM destination unverified | Match already-published asset in TASK-008; no new posting task | UNVERIFIED, no asset-level paid attribution | Grok/Praxxis |
| Free destination → detailed Preparedness guide | 35 draft articles not independently source/safety cleared | Execute full native source crosswalk, 41/82 export checks and QD | HARD HOLD | Preparedness/independent QA |
| Free guide → optional Legacy Triage PDF | Seller ownership, relevance, sensitive credential guidance unverified | Read actual delivered PDF and rights/privacy disclosures; ensure commercial intent fit | NOT APPROVED | Founder/Commerce |
| Product → paid order and delivery | Successful paid checkout, download, refund accounting unverified | Founder-authorized E2E merchant purchase/delivery/fee test | NOT TESTED | Commerce |
| Human campaign session → realized net revenue | No reconciled asset_id sessions, confirmed orders/refunds/fees | Compare 7/30 day cohorts with true merchant-paid orders, minus fees/refunds | NOT COMPUTABLE; never infer sales from clicks | Analytics/Commerce |

**Acceptance before any later release:** all 82 real outputs reconcile exact URLs/source-link visibility, original reading depth and safety states; explicit source and qualified safety reviews; zero false QD approvals; mobile 360/390/768/1440px link/accessibility checks; owner confirms product/merchant rights and privacy handling; explicit founder release authorization. Net revenue per 1,000 qualified human sessions remains **NOT COMPUTABLE**.

No WordPress/CMS, navigation, homepage, merchant, affiliate, email, analytics, social, Grok task queue, purchase or spending changes.
