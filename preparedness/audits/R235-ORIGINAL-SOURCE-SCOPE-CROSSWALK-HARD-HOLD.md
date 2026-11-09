# Preparedness R235 — independent shared-source review docket (2026-11-09 PT)

**Scope:** Issue #136 source/citation custody only; charter #818 and conversion issue #820 cross-referenced. **State: DRAFT_HARD_HOLD**. This is not approval to merge, edit original manuscripts, release WordPress drafts, certify a source, resolve a citation or promote a product. No navigation/CMS/merchant/social changes.

## New deterministic gate
`tools/r235_crosswalk_receipt_hold.py` independently reconstructs the source-URL/scope worklist from all eight exact original contributor source files, compares Git-blob identities and complete source rows against the frozen crosswalk's row-index, origin, ID and supports fields, detects duplicate IDs and missing shared URLs, and emits a sorted review queue with per-group evidence SHA-256. It accepts **terminal slash equivalence for grouping human review only**—not for merging contributor claims. This matters for NCHFP's jerky URL: the hist-food reading has a slash and distinct source ID, while the base/food readings have no slash. This is a known alias; changing it or assigning the content to one alleged canonical scope would lose original evidence.

The guard is authenticated by exact blob in R220 and called before the renderer even in originals-only mode. A postflight pin check rejects replacement of the guard during audit. It always returns `DRAFT_HARD_HOLD`; a named review receipt is **not** independent QD/safety or publication permission.

## Authenticated input reconnaissance (connector reads of R234 HEAD)
- Frozen crosswalk: `preparedness/sources/crosswalk.json`, Git blob `d62e493a67dedd23e04cfdf3cce762ef933c6bf9`.
- **244** raw contributor rows across **8** original files, all observed Git blob pins matched.
- **202** exact source URLs; **32** exact duplicate-URL groups; **15** duplicate-ID groups (same ID across contributing rows); **32** review-alias shared-URL groups.
- All 32 shared groups are currently **pending independent human source/reading-scope review**. All 32 contain differences in `supports` text, which may reflect reading scope rather than factual contradiction. **20** show differences in verification-date values. **0** groups have all member rows marked `human_link_check=true`. None is automatically reconciled.
- Risk-first review cluster: Ready.gov power-outage fact sheet used under four distinct contributor IDs; CDC power-outage and Ready.gov disability/power/plan shared across three contributors; NCHFP jerky trailing-slash alias with materially different recorded reading depth, and contemporaneous USDA FSIS guidance to reconcile in human review. Preserve variant sources and claims intact.
- Article #7 `cdc-find-clean-water` ×2 and Article #20 `start-ready-plan` ×1 original citation occurrences remain held. Seven historical source identity conflicts and E235 Article #7 proposed water-safety changes remain human/editorial work, **not** machine-resolved by this gate.

## Execution evidence / limitations
- **42/42 local synthetic Python tests PASS** against the independently constructed R235 implementation, including 36 targeted provenance-mutation failures; Python compilation PASS.
- Source/test GitHub files and R220 integration are committed on an isolated stacked branch; tests **have not executed against the exact remote commit in the full native repository**. The actual eight-source census was independently reconciled by connector reads, not by running the committed Python on the complete checkout.
- **NOT EXECUTED:** authentic local `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, inherited full suites, all 35 articles / 6 tools, genuine 82 article/tool WordPress-preview HTML outputs, independent QD and qualified water/food/medical review. Local GitHub DNS prevents a trusted native checkout. No publication.

## Conversion-first Preparedness acceptance
One **candidate audience/topic**, not a Grok production order: household out-of-area emergency contact and essential documents → authentic live free official resource landing `https://finalvestige.com/preparedness/` → *optional* Legacy Triage only **after** buyer-intent fit, merchant ownership/rights, file privacy and secure handling, disclosure, checkout, delivery and refund verification. Legacy Triage's estate/incapacity PDF may be a poor direct fit for generic disaster traffic; never auto-insert it into the draft Archive. Do not reintroduce retired water freebies. Draft on-site CTA remains **HOLD / NO DEPLOY**.

Acceptance: independently identify a genuinely published, rights-cleared Grok `asset_id`, actual platform post URL, `utm_campaign`, mobile destination and claim/guide consistency through existing TASK-008. Check live free-guide visibility and no forced email gate. Only after authorized offer verification, separately QA mobile CTA disclosure, destination, merchant acceptance, fulfilled file, refunds and access/privacy. Capture qualified-human sessions → landing → relevant CTA → provider-confirmed lead (where applicable) → independently settled order → fees/refunds → realized net revenue. No new scripts; no attributed orders or lead counts invented. 7/30d net revenue / 1,000 qualified humans **NOT COMPUTABLE** with missing denominator and settled order ledger.

## Strict owners / release
Preparedness integration and citation gate: Issue #136. Grok owns creator production, Praxxis owns independent published asset QA and TASK-008, Claude owns core website/analytics production, commerce/founder validates rights/offer and approvals, independent safety/QD must adjudicate claims. All PRs draft. No CMS, WordPress, navigation, merchant, affiliate, email, social, paid service or release changes.
