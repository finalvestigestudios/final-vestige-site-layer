# R306 — Authentic 35-article lineage crosswalk · DRAFT / HARD HOLD

**Owner lane:** Preparedness Archive integration and source/citation safety gates only · Issues #136 and #820 · 2026-11-11 (Pacific).

## Authenticated witness (not release certification)

- Exactly **35 articles / 70 source files** observed in the GitHub contents listing at R305 HEAD `99eacc58aa9127bfbdd0b6646decfd6e41ca664a`. Crosswalk file: `r306_live_lineage_35_articles_HARD_HOLD.json`. Each file records frozen R200 Git blob SHA, integrated Git blob SHA, source cluster and canonical route.
- R200 source manifest Git blob: `5822f9dfde21d1f3bdfc26658769d852c639438c`; seven branch heads were individually compared with their frozen SHAs and each result was **identical / 0 ahead / 0 behind** at this check.
- **18** articles have identical frozen body and metadata blobs; **5** changed body only; **3** changed metadata only; **9** changed both. Therefore **14** body and **12** metadata differences, of which **9** overlap. These numbers are custody distinctions, not quality or safety verdicts.
- **4 body differences are LF-vs-CRLF only**, established by reading both exact GitHub contents and comparing after replacing CRLF with LF: `root-cellars-cool-storage`, `navigation-before-gps`, `sanitation-before-germ-theory`, and `pioneer-supply-chains-failed`. The fourth also changes metadata; that metadata is NOT cleared.
- **10 body revisions remain substantive and unadjudicated:** `household-emergency-plan`, `three-day-kit`, `outage-heat-cold-generators`, `home-fire-escape-plan`, `shelter-or-evacuate`, `family-communication-plan`, `go-bags`, `preparedness-real-households`, `pioneer-travel-rations`, and `pemmican-and-dried-meats`. Changed source/citation identifiers in the final two historical articles require explicit reading-scope and primary-source crosswalk review; not merely a copy-edit.
- New read-only gate checks per-row exact integrated Git blob bytes, R200 lineage, duplicate/canonical routes, 35/70 completeness, symlinks, unaudited inputs and false safety/commerce approval. It intentionally returns `DRAFT_HARD_HOLD` even when all exact files match.

## Examples to prioritize for qualified QA

1. `three-day-kit`: the power-outage food-safety passage changes which agency's time/temperature threshold is quoted and changes cited sources. **Qualified source review required.**
2. `shelter-or-evacuate`: hazard guidance is materially reframed around official instructions, warning time and individual location. Validate emergency authority wording.
3. `home-fire-escape-plan`: a new claimed reading of a USFA printable grid and a link to a worksheet appear. Verify that source reading and the target draft/rights.
4. `family-communication-plan`: CDC chemical-emergency communication evidence is added; verify it actually supports the scope of each claim and does not imply text-to-911 is universally available.
5. `pioneer-travel-rations` and `pemmican-and-dried-meats`: `nchfp-jerky` citations are replaced with `hist-food-nchfp-jerky`, changing source identity. Preserve contributor-specific scope; compare full original records and URLs.

## Executed vs blocked

- R306 local: **75/75 synthetic Python tests PASS** on exact source/test Git blob identities (verification with `git hash-object` and connector `fetch_file`); Python compilation PASS. An incomplete local checkout correctly fails `INVALID_HARD_HOLD`, exit 1.
- The **full authenticated native** `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py` and 41 WordPress draft export comparisons were **not executed** because the local GitHub checkout cannot resolve `github.com`; GitHub file reads through the connector are not a substitute. The prior R305 903 synthetic tests were not re-run here.
- Independent QD PR #157 remains draft; synthetic-fixture PR #169 remains draft and still contains one `_dup_test.json` write in the actual source directory. Do not conflate PR #169's first isolated test with complete fixture isolation.
- Article #7 water-treatment warnings and Article #15 / Tool #104 emergency dispatch, children, no-JS, privacy, printing and accessibility holds remain. No independent source/safety or QD PASS.

## Conversion-first experiment / approval boundary

**One audience:** households seeking family communication and reunification preparedness. **Free destination candidate:** existing `https://finalvestige.com/preparedness/` official resource/archive page. Candidate draft CTA: **"Make a plan for how your household will reconnect. Start with free preparedness resources."**

No authenticated already-published Grok family-contact `asset_id`/permitted mobile destination has been matched in TASK-008. Tool #104 cannot be recommended as cleared until independent emergency, privacy, print, no-JS and accessibility review. There is **no verified FV-owned/licensed, actively purchasable, correctly deliverable Preparedness SKU**; do not invent or activate a paid pack, reuse retired water freebies or approve Legacy Triage. Paid CTA and checkout testing are blocked by missing SKU and merchant rights/fulfillment evidence.

**Offer → funnel → blocker → change / experiment → pass/fail → owner**

| Offer / funnel | Blocker | Proposed acceptance experiment (draft only) | Evidence / owner |
|---|---|---|---|
| Grok social topic → free resource | Unknown published asset ID, destination & audience match | Verify existing asset ID, dates, permitted URL and 360/390px landing before a new campaign | NOT VERIFIED · Grok/Praxxis |
| Free guide → optional printable card | Tool #104 safety and privacy claims held | Qualified claims/source crosswalk, real browser print/no-JS, mobile accessibility and child-data handling | HARD HOLD · Preparedness QA |
| Free guide → optional purchasable practical pack | No rights-cleared SKU, merchant terms, checkout or deliverable proof | Founder/Commerce select **one existing** real product, verify license, purchase, receipt, refund/support and honest disclosure before draft paid CTA | NOT APPROVED · Founder/Commerce |
| Qualified sessions → paid order → net revenue | No authenticated orders, settlement, fees/refunds or Grok mapping | Reconcile `utm_content=asset_id`, 7/30-day qualified-human cohorts, independently verified orders, gross minus refunds/fees | NOT COMPUTABLE · Claude/Commerce |

Net revenue per 1,000 qualified human sessions remains **not computable**. An affiliate outbound, session, checkout start or signup is not a confirmed paid sale.

No merge, public page, navigation, CMS, storefront, plugin, social, email, analytic script, affiliate activation, spending or other agent's queue was changed. Founder retains production release authority.
