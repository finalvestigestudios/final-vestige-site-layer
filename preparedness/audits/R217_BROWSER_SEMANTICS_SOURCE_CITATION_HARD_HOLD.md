# R217 — WordPress citation navigation and release-language integrity (DRAFT / HARD HOLD)

**Custody:** Preparedness Archive #136 only; conversion coordination #820 / charter #818. **Base:** R216 draft PR #1582 exact HEAD `1a3f170a8e4db39076edf4d7fb2560c4b58cfb22`. Isolated child branch; NO MERGE, CMS, public publishing, homepage/nav, WordPress editing, social content/posting, mail, affiliate activation, analytics deployment, merchant change, purchase, spending or QD/medical-safety PASS. This document is an engineering audit, not an approval.

## Independent QA finding addressed

A new independent review of R216's Python HTML parser identified three real **synthetic transport bypasses** even though original authored-source protection remains HOLD:
1. `dict(attrs)` retained the **last** duplicate `href`, `style`, `class`, `aria-hidden` or `id`; browsers can honor the first attribute. A first `href="http://..."` followed by last `href="https://..."` could pass source-link checks and navigate to the first target.
2. Duplicate `id="src-1"` outside the bibliography can intercept a citation's in-page link; checking only bibliography list IDs is insufficient.
3. False-release checks did not normalize whitespace, so `Approved  for publication` or a line-break-separated equivalent could evade exact-phrase detection.

**R217 implementation:** `preparedness/tools/r217_transport_semantics_guard.py` performs a second independent, read-only whole-document HTML pass over Article #7 and #20 **both WordPress and preview**. It requires an R216 exact four-transport `DRAFT_HARD_HOLD` report, explicit false release flags, `source_claim_review=REQUIRED` and matching SHA-256 transport receipts. It rejects **all** duplicate HTML attribute names before dictionary conversion, global duplicate/empty IDs, unresolved fragments, source-citation targets outside numbered bibliography list items, and whitespace-normalized false-publication assurances, including elements spanning inline tags. It returns only `DRAFT_HARD_HOLD` (CLI exit 2) or `INVALID_HARD_HOLD` (exit 3). No output files are written.

**QA/limitations:** The appended stage must be deliberately included in the eventual integrated gate. Executing R216 alone does not automatically execute R217. R216 report JSON is structurally authenticated against local bytes and labels, not independently signed by GitHub; original R214→R215→R216 provenance remains mandatory. No computed CSS, browser navigation, WordPress sanitization, native full build, source-truth, independent QD, emergency-medical review or live fulfillment is established. No original article/source register/taxonomy/URL/safety-classification bytes were edited.

## Verification and frozen contributors (November 8, 2026)

Run locally, independent synthetic fixtures only:
```sh
python -I -m unittest discover -s preparedness/tests -p 'test_r217*.py' -q
python -m py_compile preparedness/tools/r217_transport_semantics_guard.py preparedness/tests/test_r217_transport_semantics_guard.py
# For verified native checkout, additionally:
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

- **107/107 local Python synthetic tests PASS** (including 92 generated mutation tests across both articles and both transports), Python compilation PASS. Exact locally executed source and test Git objects match commits by `git hash-object`; positive fixture exits `DRAFT_HARD_HOLD`, a recomputed-digest duplicate-`href` attack exits `INVALID_HARD_HOLD`.
- **Native original repository build / full 35-article corpus / 41 WordPress targets: NOT EXECUTED.** Local `git ls-remote` failed: `Could not resolve host: github.com`. Connected GitHub API can read/write approved draft files but is not a complete executable repository checkout.
- **Core seven frozen Claude contributors:** start `2122d856fce9f64887c16df3d52e64be9f59a55b`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; historical field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; historical food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; historical home `7504a5f099594d635e3dd7332a33a2e1346c43a2`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`. Additional shelter continuation `ac8625faf30dd5538fadc31e06cb5a2cea1defae`; follow-up `6a5998ead97eca997e573ce8d3ceacf1c6aabad4`. All checked as source-of-truth refs, **not merged** into this branch.
- **Independent QA:** #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` older Start Here article/test changes; #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` isolated source fixture; stacked #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` second isolated fixture, all DRAFT/OPEN. Source integrity preserved: do not cherry-pick article files blindly over newer Claude warnings. Independent native test execution remains unverified.
- **Homepage engineering:** latest #1587 `c991f5f5a7288a81ce4b24ed7cb5ebf2b3abdc4d`, stacked on #1580 `b1a6b8c4ebe0fca4ee9a4755ac4913b5063bc619`; untouched.
- **Existing source exceptions:** Article #7 contains two unexplained CDC citation occurrences, Article #20 one unexplained Ready.gov occurrence, plus seven historical source-ID conflicts. These are still open; R217 does not review or resolve them. **35 original article canonical routes and 41 export targets are *inherited/protected but not freshly native-verified*.** No false safety clearance.

## Conversion-first, one-audience acceptance matrix — INACTIVE

**Audience hypothesis:** households arranging family contact, identity, insurance and essential-document locations in advance. **Authentic free destination:** https://finalvestige.com/preparedness/ publicly offers source-backed agency references without signup or purchase. **Provisional commercial candidate:** https://payhip.com/b/n1RhV, Legacy Triage, Vested Wisdom seller listing, $19, PDF printable advertised; a public listing is not authorization, settled sale or delivery. Its account-access worksheets create sensitive-data custody risks. This is NOT approved FV fulfillment or a published affiliate offer.

| Offer → funnel step | Blocking evidence | Draft-only change / experiment | PASS/FAIL evidence | Owner |
|---|---|---|---|---|
| Grok high-intent household-records video → free Preparedness Archive | No matching authenticated published asset_id, exact hook, platform/post URL, consent or destination in TASK-008 | Ask Praxxis to reconcile existing Grok inventory without changing creator queue | UNVERIFIED | Grok/Praxxis |
| Free official planning links → optional household planning resource | Detailed original guide/citation/safety review not cleared | Keep official sources accessible, validate 360/390 px and keyboard/screen-reader source links in staging | Public archive LIVE; original article HARD HOLD | Preparedness/QA |
| Free Archive → optional $19 Legacy Triage printable | Seller rights, product claims, credential privacy, FV commercial authority, returns/refunds unclear | Independent offer review; label optional, nonessential, and *separate* from public guidance | Listing OBSERVED; sale/rights/checkout/delivery NOT VERIFIED | Founder/Commerce |
| Product CTA → paid order & download | End-to-end real purchaser, secure PDF, tax/fees, delivery and refund proof absent | Merchant-authorized buyer-path test, receipt, download and refund-policy check | HARD HOLD; do not enable CTA | Commerce |
| Qualified human campaign sessions → realized net revenue | No asset-level attribution or merchant-confirmed payments, fees/refunds | Reconcile 7/30-day cohorts via pre-existing privacy-approved measurement; don't add scripts | NOT COMPUTABLE, not zero | Analytics/Commerce |

**Inactive draft CTA (not a link and not for a live page):** “Begin with free official emergency-planning resources. If a separate family-records organizer would help, an optional paid printable is under review. Nothing in the free Archive requires a purchase or signup. Keep completed financial or account-access records securely stored, never in publicly shared files.”

**Campaign acceptance:** human-approved published asset and matching factual hook; actual post URL/asset_id/allowed UTM; destination HTTPS and canonical route; original guides withheld until verified; legible citations/safety notes; mobile 360/390/768/1440; accessible consent and disclosure; privacy of sensitive records; merchant acceptance, secure checkout, receipts, actual fulfillment, refund handling, and verified transaction data before revenue claims. **Net realized revenue per 1,000 qualified human sessions = NOT COMPUTABLE** until qualified sessions and merchant-confirmed net revenue exist. Do not mistake clicks, impressions or signup for orders. 7/30-day cohort denominators and tiny-sample warnings mandatory.

**Next integration gate:** independently validate the exact authentic original corpus, reconcile #157/#169/#973, run native validate/build/full tests, exercise this R217 stage behind R216 against all authentic generated Article #7/#20 outputs, and adjudicate source exceptions. No synthetic PASS substitutes for any reviewer approval.
