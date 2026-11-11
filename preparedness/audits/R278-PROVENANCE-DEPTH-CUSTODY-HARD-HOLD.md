# R278 | Commit the R277 provenance/depth safety gate and adversarial tests — DRAFT / HARD HOLD

**Scope:** only Preparedness Archive integration/source and citation custody in #136. Founder conversion coordination #820. **No publication, production, commerce or QD approval.**

## What this adds

- `tools/r278_reconciliation_guard.py` is a **read-only, fail-closed** four-ledger integrity gate for authenticated R200 contributor custody, R275's protected 96-file integrated snapshot (recorded by R276), R277's provenance correction, and the R277 article-depth witness. All four source documents are checked against exact committed Git blob SHA-1 OIDs before analysis.
- `tests/test_r278_reconciliation_guard.py` is a committed **70-case** deterministic Python suite: six positive/format/hold checks and 64 synthetic mutations across missing records, duplicate URLs/slugs, changed source OIDs, damaged reading-depth metrics, lost citation IDs, false seven-branch drift, fake QD/medical/privacy approvals and contradictory hold states.
- This validator cross-joins **all 35 R200 article routes** with the **70 integrated body/metadata entries** within the 96-file snapshot and requires an explicit, exact 17-article discrepancy docket (**14 changed bodies, 12 changed metadata**). The 14 body changes must each have a matching source-pinned depth witness.
- It preserves the six historically shorter-in-bytes article bodies (24, 25, 27, 32, 33, 34) and does **not** treat unchanged word/heading/citation counts as substantive editorial or safety clearance.
- Original R200 contributor branches compared to their *true* frozen heads all still match **7/7** (0 ahead, 0 behind, verified this run). R276's earlier claim of five **newly** drifted branches came from comparing older crosswalk provenance and was corrected in R277; do not start new intake work for that false alert.
- All current source review and release holds stay unchanged: **32 URL-sharing groups, 15 duplicate source-ID groups, three disputed CDC/Ready.gov citation occurrences, Article 7 chemical-contamination wording, Article 15/Tool 104 privacy, physical printing and accessibility**.

## Evidence and explicit limits

**Executed locally** against byte-identical source and test modules: Python `unittest` **70/70 PASS** and `compileall` PASS. Both module Git blob identities were checked against committed branch contents. The tests use **synthetic fixtures** and do not establish native repository validation or medical/editorial safety.

**Independent connected-GitHub source-record reconstruction** of the four authentic pinned JSONs: 35 distinct R200 numbers, 35 distinct original routes, 96 integrated files, zero missing article body/meta entries, 17 historic differences (14 body/12 meta), 14 matching depth witness rows, and six shorter-bytes bodies; **zero cross-document OID/route/byte discrepancies** in the bounded reconstruction. This is a cross-record audit, **not a Python native full-tree pass**.

**Blocked:** complete repository checkout via container DNS resolution of github.com; thus full `validate.py`, `build.py`, inherited regression suite, 41 authentic WordPress draft exports and the new validator's `audit(root)` against the complete repository **NOT EXECUTED**. Existing Github Actions failed without diagnostic logs; no false PASS. The newly committed validator does not change or bypass R220's existing immutable producer and draft-export gates. It is an **additional independent pre-export check**, not an authorized new publisher.

Reproduce in a complete, authenticated checkout from the `preparedness/` directory:

```bash
python -m unittest discover -s tests -p 'test_r278_reconciliation_guard.py' -v
python tools/r278_reconciliation_guard.py --root .
# Must report DRAFT_HARD_HOLD; never publication PASS.
# Run inherited project validation/build and all export assertions separately.
```

## Offer → step → blocker → change/experiment → evidence → owner

| Offer | Funnel step | Blocker | Change/experiment | Current evidence | Owner |
|---|---|---|---|---|---|
| Existing **public** free Preparedness Archive | One published family-contact/reunification Grok asset to mobile landing | No authenticated asset ID / rights / native destination packet in TASK-008 | Grok/Praxxis verify already-published asset/date, UTM, signed-out mobile click; do not post or retask | **NO VERIFIED MATCH** | Grok/Praxxis |
| Source-backed free guidance | Article to optional, clearly marked practical resource | Article 15 and Tool 104 child-information/print/accessibility concerns | Independent qualified reviewer assesses safety, print, data capture, accessibility and appropriateness | Source custody only; **HARD HOLD** | Preparedness/independent QA |
| Provisional existing **Legacy Triage PDF** | Free guide to optional paid pack | Product rights, preparedness fit, sensitive data, seller fulfillment and founder authorization not verified | Independently audit full product and payment/refund flow *before* any public CTA | **NOT APPROVED**, no published offer | Founder/Commerce |
| Approved product (if any) | Checkout → verified paid order | Merchant-confirmed orders/fees/refunds and attribution unavailable | Authorized merchant acceptance, seven/30-day cohort reconciliation, no synthetic purchases | **NOT TESTED** | Commerce/Analytics |
| Owned audience | Confirmed signup → paid conversion | Confirmed lead and paid orders cannot be joined reliably | Consent-compliant reconciliation with existing tools, no duplicate scripts | **NOT COMPUTABLE** net revenue/1,000 qualified-human sessions | Analytics |

No retired water freebie, unpublished article/card destination, new offer, affiliate activation, CTA, analytics script, merchant, WordPress/CMS, social post or email was created or changed. No claimed sales, checkout conversions or net revenue.

**DRAFT / HARD HOLD / NO QD PASS / NO MEDICAL SAFETY VERDICT / NO RELEASE.**
