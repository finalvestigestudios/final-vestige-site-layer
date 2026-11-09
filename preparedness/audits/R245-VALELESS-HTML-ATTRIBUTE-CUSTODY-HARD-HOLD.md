# R245 — Valueless HTML attribute boundary repair, strict citation-custody hold

**Date:** 2026-11-09 PT. **Scope:** Preparedness Archive Issue #136 only. Cross-reference commercial charter #818, measurement issue #820, Praxxis/Grok TASK-008. **DRAFT / HARD HOLD. No WordPress/CMS/navigation/site/merchant/affiliate/email/social/analytics/spend writes. No publication, medical safety, source adjudication or independent QD PASS.**

## Independent QA finding and negative control

Praxxis' 2026-11-09 dated handoff found R242 gate rejected valid HTML with a *valueless* attribute preceding another attribute. Reproduced against original authenticated R242 Git blob `2deedb8df74badf6b149719f71bb43e515993054`:

- `<p data-reviewed class="visible">{{cite:source}}</p>` → incorrectly raised `R242 missing HTML attribute separator`.
- `<p title="ordinary"aria-hidden="false">{{cite:source}}</p>` → correctly rejected as missing required separating whitespace.

R242 consumed HTML whitespace while looking for an equals sign; when no equals followed the valueless attribute, it discarded the valid separator before checking for adjacency.

## Bounded correction

Update the existing `preparedness/tools/r240_html_attribute_entity_custody_hold.py` rather than add a redundant validator. Retain the end of the attribute name; if it is valueless (no equals), restore the scanner position to that boundary so the existing strict separator check recognizes real whitespace. If equals is present, retain the full existing quoted/unquoted value path.

The amended module Git blob is `156f475b88c1e374e4626119ec1e9965474ec329`; the R220 authenticated loader is repinned from original `2deedb8df74badf6b149719f71bb43e515993054` to this exact revised blob. R220 loader's new Git blob is `2669ed5599ff259cd8ba9466686feb30eb44ae6a`. The new R245 tests have Git blob `ab444f618c4e07ed7928366a46c449030fbcc9e1`.

No changes to any original contributor manuscript, body/metadata Git identity, source-use explanation, canonical URL, safety label, six tools, taxonomy or original frozen source crosswalk.

## Executed verification and explicit limitations

- Reproduced the original false rejection and the genuine missing-separator rejection on a **byte-exact local copy** of the authenticated R242 module (verified original Git blob above).
- **225/225 local Python tests PASS**, comprising all **95/95 unmodified exact R242 regression tests** (Git blob `c8d72d13968b6ed6dce2b6e6017e81ceba750788`) plus **130/130 new R245 syntactic-custody tests**, against revised module whose `git hash-object` is the same as the committed module `156f475b88c1e374e4626119ec1e9965474ec329`. New R245 test module's local Git object equals the committed test blob `ab444f618c4e07ed7928366a46c449030fbcc9e1`; `python -I -m py_compile` PASS.
- Regression families: 48 distinct valid valueless separators across eight tags/six whitespace variants; 48 paired malformed adjacent quoted-attribute controls; 24 individually encoded visibility controls; 10 additional custody tests including five HTML whitespace controls, duplicate class, quoted metadata, C0 controls and 35-record synthetic roster fail-closed mutation.
- Existing R242 encoded class/id/style/aria-hidden controls, duplicate visibility keys and zero release flags preserved. **Do not treat test counts as independent editorial acceptance.**
- Current frozen source contributor heads independently compared to their original manifest: **7/7 identical**. Original static corpus from parent integration: 35 bodies / 2,000 citation occurrences; R245 does not change those files.
- Independent QD draft PR #157 at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` and synthetic fixture draft PR #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5` inspected, untouched. Homepage lead #1689 checked at `f55c36b6598eec558dd8bb24e4c8988becc51be0`, untouched.
- **Full native checkout unavailable:** `git ls-remote https://github.com/finalvestigestudios/final-vestige-site-layer.git HEAD` fails `Could not resolve host: github.com` in local runtime. Thus native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, inherited complete unittest suite, exact WordPress/preview exports, browser behavior, independent source and qualified safety review **NOT EXECUTED**. Connector-fetched Git blobs and local synthetic tests do not substitute.

## Remaining source/safety holds

Retain **32 shared-source review groups** and the three disputed original citation occurrences (two CDC references Article #7; one Ready.gov reference Article #20) as unapproved. No claim-level human/source approval, medical safety certification, independent QD PASS, merchant approval or permission to merge/publish.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE / TEST → PASS/FAIL → OWNER

| Offer / funnel | Blocker | Change / acceptance test (draft only) | Evidence/state | Owner |
|---|---|---|---|---|
| Existing ungated public Preparedness Archive → verified household-contact planning guide | Original Article #1 is not public; no credible matched Grok asset ID | Verify the existing public official-resource link, then original draft readiness; do not promise unavailable guide | Public shell exists; custom source-checked guide HARD HOLD | Preparedness / independent QA |
| Real Grok video → free destination | Authentic published household-contact asset, original hook, rights, URL/mobile click route and approved UTM absent | Praxxis/Grok inspect **already-published** posts in TASK-008, record asset_id and signed-out mobile 360/390px path; no new queue item | UNVERIFIED | Grok / Praxxis |
| Free guidance → optional paid practical pack (Legacy Triage, **provisional only**) | No verified suitability, complete PDF, rights or safe sensitive-information handling | Founder/Commerce assess purchased-rights/fulfillment/actual contents and explicit positioning; otherwise omit upsell | NOT APPROVED / NOT A VERIFIED PREPAREDNESS OFFER | Founder / Commerce |
| Paid CTA → confirmed checkout/delivery | Actual checkout, taxes/fees/refunds, mobile accessibility and delivery untested | Only authorized transaction + invoice, delivery receipt and refunds reconciliation | NOT TESTED | Commerce |
| 7/30d qualified-human sessions → confirmed paid orders → net revenue | Missing verified unique asset, session, purchase, refunds/fees data | Reconcile existing consent-compatible event sources; separately label outbound clicks, confirmed leads and merchant paid orders; do not add duplicate scripts | NO ATTRIBUTABLE PAID CONVERSION; KPI NOT COMPUTABLE | Analytics / Commerce |

**Decision:** source/citation-custody repair BUILT and isolated TESTED; archive publishing, commercial activation and release remain **HARD HOLD**. Net revenue per 1,000 qualified human sessions is not computable; missing evidence is not a zero-sales claim. No retired water lead magnet or speculative commercial offer introduced.
