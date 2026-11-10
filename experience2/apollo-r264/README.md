# Apollo Experience 2.0 — R264: source-matched text reflow + conversion custody (STAGING HOLD)

**Scope:** Independent Apollo component QA descended from draft R263 PR #1910, not homepage PR #49 or Research Desk PR #158. No WordPress, merchant, analytics, social, or email writes. Nothing here is authorized for deployment.

## Evidence and execution

Executable: `qa/zoom_conversion_acceptance.py`. Requires Python Playwright, Chromium, PHP, the exact sealed R238 fixture, the R262 overlay and R263 PHP mock. Do not substitute synthesized HTML: the test executes real R224/R262 PHP in the R263 WordPress simulation, checks source SHA-256 and relevant Git blobs, then uses the PHP output for Chromium.

```bash
python experience2/apollo-r264/qa/zoom_conversion_acceptance.py \
  --fixture fixture/sealed-r238 \
  --overlay experience2/apollo-r262 \
  --mock experience2/apollo-r263/qa/wp-real-source-sequence.php \
  --out QA-R264
```

Two independent local runs: **30/30 Chromium contexts per run**, 320/390/768/1440/1920 px × root text size 100/200/400% × JS enabled/disabled; 55 NASA links, all in-document fragment destinations, exactly one existing free-investigation link, zero merchant links, no off-screen page overflow or unexpected resource requests; keyboard SourceDrawer with JS and native `<details>` without JS. Four 200%-text screenshots were byte-matched across runs. A deliberately introduced 900px min-width overflow at 320px was detected.

Stable receipt hash (content-normalized): `fd58f83b44b4558eb8ee6f9907f592be5dd1b3219a6751a5db5cd0bb887752e9`. Full `receipt.json` SHA-256: `e62e47763928041537e9cd661b811748ea3ea3e0e7776465d4c152fd0487a25a`. This is **root-font-size stress**, NOT browser UI zoom, installed WP, network LCP/CLS, or axe-core. Such claims remain blocked. The test does not alter protected content.

## Historical/rights boundary

Primary authority: [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). The most probable ignition initiator was an electrical arc; **no single ignition source was conclusively identified**. Do not imply otherwise. No synthetic geo-pin claims. [NASA advertising guidance](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) prohibits implying NASA endorsement of commercial offerings and cautions against unauthorized use of identifiers and recognizable people in ads. A NASA source link does not confer product-image or testimonial rights.

## One optional conversion pathway — PROPOSAL ONLY

**Audience:** Grok long-form Apollo viewers who continue into evidence-based space-history collecting. **Entry:** one unique Grok `asset_id` / `utm_content` and verified actual post URL (currently unknown) → existing original [Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) via evidence Atlas → *after completing the article*, one plainly marked optional link to Final Vestige's [Collection guide](https://finalvestige.com/collection/) explaining Mini Museum specimens. The existing Collection page publicly describes the Mini Museum guide and a commission disclosure. **Do not call meteorites or collectibles Apollo mission relics**, and do not insert the offer into the historical source narrative. The final product/merchant destination, affiliate acceptance and settled revenue are NOT verified here. No link is added by R264; commercial activation is prohibited pending founder and Claude release clearance.

**Hypothesis:** qualified space-history readers who choose a separately labeled specimen-information guide after reaching the original investigation may show higher *merchant-verified paid conversion* than readers offered unrelated goods. Test against an unmodified editorial baseline only after approved integration, with no dark patterns or deceptive urgency.

**Measurement:** unique `asset_id`, `utm_source`, `utm_medium=organic_social`, `utm_campaign=history_pilot_2026_11`, `utm_content=<asset_id>` → qualified-human landing session → independently observed guide CTA → disclosed outbound merchant click → merchant-verified paid order/commission → subtract refunds and fees → realized net revenue. 7/30-day cohorts. Principal KPI: net revenue / qualified-human sessions × 1,000 (not computable without both authenticated terms). Distinguish outbound click, signup and checkout attempt from purchase; report low-N warnings. No new scripts or tracking cookies authorized.

## Prioritized offer / step / blocker / experiment / evidence / owner

| Offer | Funnel step | Blocker | Change / experiment | Evidence / state | Owner |
| --- | --- | --- | --- | --- | --- |
| Mini Museum via FV Collection | Purchase and net revenue | Eligible affiliate destination and settlement not independently confirmed | Check accepted account/merchant reporting before any site CTA | **HOLD**; public guide ≠ commission proof | Founder + Claude |
| Apollo documentary | Qualified landing | Grok Apollo `asset_id`, live post, actual campaign link unknown | Reconcile TASK-008 and dated handoff; preserve Grok's queue | **UNVERIFIED** | Grok + Praxxis |
| NASA Atlas → original Apollo investigation | Source review and free CTA | Text resizing and source link integrity | R264 source-verified 30-context regression | **LOCAL PASS; NOT LIVE** | Apollo Evidence Studio |
| Merchant sales → realized revenue | 7/30-day attribution | Verified paid transactions, fees/refunds and human sessions unavailable | Permissioned, privacy-respecting reconciliation | **NOT COMPUTABLE** | Claude / Commerce |

**Release blockers:** genuine provenance-verified axe-core, independent screen-reader and true browser UI zoom, installed WordPress/Assembler, actual HTTP/CSP, real mobile, field LCP/CLS/INP, hosted CI/QD, inherited R198 issue, applicable imagery/offer-rights review and founder approval. Homepage #49 and Research Desk #158 remain isolated. Reference Issues #150, #818 and #820; TASK-008 belongs to Grok/Praxxis, not this lane.
