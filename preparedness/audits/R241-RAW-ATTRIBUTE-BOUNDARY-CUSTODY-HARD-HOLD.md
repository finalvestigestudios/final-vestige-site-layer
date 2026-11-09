# Preparedness R241 — Tokenized Attribute Boundary Custody / HARD HOLD

Date: 2026-11-09 PT. Issue #136, conversion governance #820 / charter #818.

## Finding and bounded repair

R240's broad raw-expression match could interpret a quoted descriptive attribute as if it set a real visibility-sensitive attribute. Example `<div title="class='x&amp;y'" class="visible">` was rejected because `class='x&amp;y'` appears *inside the title value*. A real class/style/id/aria-hidden character reference must still fail closed. R241 replaces the regex lookup with quote-aware raw start-tag attribute tokenization, cross-checks ordered names with Python HTMLParser, rejects malformed and duplicate sensitive attributes, and only evaluates entity spellings in the real sensitive attributes. No source, author body, source crosswalk, safety labels, canonical routes, export HTML, navigation or WordPress writes.

Preserves hard-hold gating. Existing R240 test compatibility intentionally retains the `R240` diagnostic prefix. New R241 test suite adds 55 separately counted benign quoted-string examples and 55 separately counted real encoded-sensitive-attribute negatives, plus six custody/markup controls (116 independently counted tests).

## Exact code custody

R241 revised gate: `preparedness/tools/r240_html_attribute_entity_custody_hold.py`, Git blob `bfffb168a236abc4b4923e5113c362e36e30bf76`; updated `preparedness/tools/r220_full_slate_draft_custody.py` pins that blob; 116-test file `preparedness/tests/test_r241_attribute_tokenizer_regression.py`, Git blob `c3c03b3505cc91516516e50046a907c750646883`.

Local isolated execution: `python -m unittest discover -s /mnt/data/r241/preparedness/tests -q` => **116/116 PASS**, `python -m py_compile` => PASS. Local Python source/test git-hash identities match uploaded GitHub blobs. This is NOT the complete repository. The complete authentic `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, inherited `unittest discover`, production HTML/WordPress/browser acceptance, and independent QD have NOT run against this head. Local `git ls-remote` could not resolve github.com; connector-based GitHub writes/reads worked.

## Freeze/review dependencies

Seven Claude cluster refs rechecked from actual Git refs 2026-11-09 PT; all match frozen R200: start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; historical field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; historical food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; historical home `7504a5f099594d635e3dd7332a33a2e1346c43a2`.

Independent safety PR #157 head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` is unmerged; food synthetic fixture PR #169 head `e9cd7766dac59d47ab467d8945269b9146c2aef5` remains unmerged. #169 review notes unresolved direct working-tree mutation in duplicate-ID test. Home lead PR #1689 head `f55c36b6598eec558dd8bb24e4c8988becc51be0` checked, untouched.

Claims requiring human source-level adjudication: 32 shared-source/scope groups, three original disputed occurrences (Article #7 two CDC; Article #20 one Ready.gov), and outstanding medical-device/water-treatment safety reviews. R237's 2,000 citation count and 35-article slate are **historical provenance baselines**, not rerun native evidence or source-approval receipts for R241. No false QD PASS, medical-safety assertion, or publication authorization.

## Conversion-first isolated acceptance packet (review only)

**One intent:** family emergency-contact and essential-record organization. **One free destination:** authentic existing `https://finalvestige.com/preparedness/` resource index; free official materials must remain free, no capture gate. **Potential paid offer:** existing Legacy Triage $19 PDF remains **provisional / NOT APPROVED** because disaster-specific fit, complete PDF rights and security handling, privacy language, merchant authorization, checkout delivery, refund path and net receipts have not been established. No new product or retired water guide.

Draft CTA concept on a *future reviewed page* (do not insert): “Start with the free family emergency-planning resources. An optional downloadable record organizer may be available after independent review; you don't need to buy anything to prepare a household plan.” Until approval, the optional paid element stays absent/disabled and should not suggest availability or a live link.

Acceptance sequence: Grok/Praxxis verify an actually published, rights-cleared social post with immutable asset_id, original hook, destination and mobile/bio-link handling; Preparedness/QA pass verified free destination, source audit, accessible non-gated guidance; Founder/Commerce verify optional product rights, use-case fit, contents/privacy, disclosure, refund policy and actual checkout/fulfillment via authorized test; Analytics/Commerce reconcile UTM session to verified paid order, fees/refunds and 7/30-day net revenue cohort. Never equate click, pageview, lead, checkout-start or affiliate outbound with a sale. **Net revenue per 1,000 qualified-human sessions: NOT COMPUTABLE.** No social posts, merchant actions, forms, scripts, CMS changes or spend.

**Status: BUILT / SYNTHETICALLY TESTED / DRAFT / HARD HOLD.** No change to actual release state.