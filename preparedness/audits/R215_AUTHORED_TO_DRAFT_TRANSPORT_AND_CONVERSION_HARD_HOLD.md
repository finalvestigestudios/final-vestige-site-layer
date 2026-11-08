# R215 — Authored-to-WordPress draft transport integrity (DRAFT / HARD HOLD)

Scope: Preparedness Archive integration and source/citation safety, Issue #136 only. Commercial coordination #820 / charter #818. Stacked on **R214 draft PR #1569** exact parent `406de581929b4fabb05e1a7fe41341c772a63d43`. Read-only engineering gate; not a publication decision.

## New engineering safeguard

R214 anchors two CDC claims in Article #7 and one Ready.gov claim in Article #20 to complete original authored HTML blocks. R215 addresses the *next transport boundary*: even if original R214 claim receipts remain frozen, the generated WordPress-ready `wp/*.html` or local `preview/*.html` could omit/alter words, reorder citation numbers, swap bibliography destinations or remove pending-safety disclosures.

- `preparedness/tools/r215_wp_claim_transport_gate.py` accepts an R214 HOLD-only dossier, exact original Article #7/#20 HTML **bytes**, and separately supplied WordPress/preview **bytes**. It is read-only; CLI consumes seven paths, prints JSON, exits **2 for DRAFT_HARD_HOLD** or **3 for INVALID_HARD_HOLD**, never 0/PASS.
- Verifies frozen original Git blob identities for the three held claim records; unique review receipts, exactly [7, 7, 20] order, untouched pending human source-claim state; retains source ID order and all original article body visible text including ordered citation references.
- Parses each draft's actual `.pa-body` and `.pa-sources` regions; checks one body/one sources section, one-to-one complete visible reading content, every citation occurrence's resolved ordinal, and each **held** source destination in numbered bibliography entries, independently for WP-ready and preview. Rejects lost body text, extra/missing/renumbered citations, substituted held URLs, duplicate references, hidden/active body content, missing pending-review notices, unauthorized state, malformed inputs and extra articles.
- Saves SHA-256 identities of supplied draft artifacts in the HOLD report, not in website/CMS. Does not modify articles, sources, all 35 routes, build outputs or any public site.
- Conservative scope: Article #7 and #20 held-citation draft transport *only*, **not** 35-article authenticated release parity. Existing other draft gates and human review remain mandatory; CSS-hidden content, real browser behavior and source truth are not proven by HTML parsing.

## Exact source test and build evidence (2026-11-08)

On locally mirrored **exact Git blob bytes** of these two newly committed files:
- `python -I -m unittest discover -s preparedness/tests -p 'test_r215*.py' -q`: **122/122 PASS** (17 explicit cases + 105 individually discoverable authored, WP and preview mutation cases). Baselines first assert DRAFT_HARD_HOLD; mutants must return INVALID_HARD_HOLD. No false safety QD approval or release state.
- `python -m py_compile preparedness/tools/r215_wp_claim_transport_gate.py preparedness/tests/test_r215_wp_claim_transport_gate.py`: **PASS**.
- Exact Git blob IDs: source `c8ca7eb508226669bc5546c7656d45f111c1be5c`, tests `8af35d8589195428e80015106a9b56faaec582c5`.
- These are isolated **synthetic** fixtures only. Authentic Article #7/#20 render pairs, original `validate.py`/`build.py`, full existing suite, 35 original bodies, 41 target exports, Chrome/WordPress browser, print and qualified safety/QD **NOT EXECUTED**. Local `git ls-remote` still fails: `Could not resolve host: github.com`. Connected GitHub read/write API works; a full trusted executable repository checkout is unavailable.

## Exact branch and independent QA custody

Seven named Claude contributor HEADs read 2026-11-08 PT:
- `claude/prep-start-bbfeb8` `2122d856fce9f64887c16df3d52e64be9f59a55b`
- `claude/prep-food-ccdc55` `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- `claude/prep-shelter-5e1e0e` `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- `claude/prep-health-837444` `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- `claude/prep-hist-field-9db767` `4e5caf812727953aa45e3bda2d382f2c67b6a09c`
- `claude/prep-hist-food-b81f19` `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- `claude/prep-hist-home-0e0e38` `7504a5f099594d635e3dd7332a33a2e1346c43a2`.

Independent QA PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic-fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`; stacked #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` remain draft, unmerged, and **NOT integrated by overwrite**. Home lead isolated PR #1573 HEAD `868bd71ec47f547daceadda99d8d4dddcb9fcb4c` based on PR #1568 HEAD `e8176caa9d3d1dcc5bd47f0cf6dd1b5d16d11ebf`, untouched. 35-article/41-output slate custody remains as previously reported, not authenticated by R215.

## Still open release safety blockers

Article #7 has two unresolved CDC claim-source explanations, Article #20 one Ready.gov claim-source explanation; seven historical shared-source identity conflicts remain. R215 flags transported differences but **does not decide whether the original advice is accurate, current or medically safe**. Human source review, QA negative-test equivalence, full native build/test, authentic 35/41 output parity and external link review, real WordPress browser/print/accessibility, independent QD and founder release approval all remain **HARD HOLD**.

## Conversion-first #820 acceptance plan (DRAFT, not activated)

Audience: household decision-makers organizing evacuation contact lists, insurance/document locations and family records.
Free authentic destination: existing ungated https://finalvestige.com/preparedness/ ; the detailed Household Emergency Plan and Records Map worksheet remain unpublished, not marketing destinations.
Single provisional optional paid candidate: public Payhip **Legacy Triage** listing at https://payhip.com/b/n1RhV showing $19 / seller **Vested Wisdom**; FV seller rights, purchase capability, file delivery, refunds and support not independently confirmed, so NOT approved for a paid link.

| Offer → funnel | Blocker | Change / experiment | PASS/FAIL evidence | Owner |
|---|---|---|---|---|
| Existing Grok asset → free Archive | Actual published Preparedness asset_id, hook, post URL and outbound destination unverified | Read-only reconcile TASK-008 before any UTM destination | **UNVERIFIED**, no attributed post | Grok/Praxxis |
| Free source-backed Archive → detailed FV guide | Held source/safety adjudication and actual WP/preview parity not complete | Execute authenticated 35/41 and qualified review; new R215 subset transport test | **R215 synthetic PASS / original HOLD** | Preparedness/QA |
| Optional Legacy Triage → merchant | Seller authorization, relevance, accurate disclosure, mobile CTA and legal terms unknown | Founder/Commerce verifies rights, listing, suitable copy, return terms | **HARD HOLD**, public listing only | Founder/Commerce |
| Merchant checkout → delivered order | Payment/fulfillment/refund/reporting untested | Founder-authorized payment/delivery audit with appropriate private account | **HARD HOLD**, no paid order verified | Founder/Commerce |
| Qualified session → confirmed net revenue | No Grok asset-linked 7/30-day human session denominators or merchant order/fees/refunds data | Reconcile existing consent-respecting native analytics to merchant-confirmed orders; no duplicate script | **NOT COMPUTABLE**, not $0 | Claude Analytics/Commerce |

No new download, speculative SKU, retired water giveaway, paid CTA, posting, newsletter, analytics script, affiliate link, checkout attempt, WordPress/CMS/navigation write, public publication or spending. **DRAFT / HARD HOLD**.