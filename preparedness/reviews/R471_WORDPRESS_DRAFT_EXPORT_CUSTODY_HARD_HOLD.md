# R471 — deterministic WordPress draft export custody (Issue #136)

**DRAFT / HARD HOLD / NOT A PUBLISH OR QD PASS**. Parent R470 PR #3052 head `82981ada3887176a69f5ab8999ed1b8ed956b12c`. Conversion governance #820 / charter #818. Only additive `preparedness/**` files; original 35 body/metadata pairs, source registers and reading scopes untouched.

## Specific safety/reader-value gap

A source/citation/crosswalk validator can pass on *input* while a generated WordPress HTML block or private preview is stale, truncated, reordered, or differs from the manuscript that was reviewed. This new read-only gate recomputes every article, populated hub and landing page from the authenticated original deterministic builder, then verifies the complete actual `build/wp` and `build/preview` inventories **byte-for-byte**, including the per-article original citation URLs, source-use limitations, safety-review notices, contextual wording, links, JSON-LD, CSS wrapper and reading depth. The 35 originals cannot disappear from the report; duplicate canonical URLs fail. Hidden or extra generated files and altered release claims fail.

The tool loads R470 (Git blob `9a34357c68463b1ab4cc60f1024711455bf23043`) and the original native `build.py` (Git blob `349173d1e1d735eade218d95c7a0a2649c8cccd9`), never an alternate code source. R470 in turn chains inherited citation/source/style guards. Local generated files must be separately produced first with `python -I preparedness/tools/validate.py` and `python -I preparedness/tools/build.py`; R471 only reads and audits them. Run: `python -I preparedness/tools/r471_wordpress_export_custody.py --root preparedness`.

## Evidence boundary

* 59 new independently named synthetic test cases are committed in `preparedness/tests/test_r471_wordpress_export_custody.py` (7 explicit methods + 52 generated methods). **Exact-committed tests not executed in this environment** because complete authenticated checkout is not locally available. Do not claim PASS pending a real run.
* An **independent local equivalent prototype**, different from committed R471, ran 65/65 Python unit methods PASS. This validates the approach, **not** the committed GitHub source/test blobs or authentic manuscript exports. The genuine `validate.py` and `build.py` were not run here.
* Nine original contributor Git refs were individually re-read and match frozen SHAs in R460, with 35-article source disputes unchanged.
* QA #157, synthetic fixture #169 and dependent repair #2205 remain independent draft/unmerged; neither supplies QD signoff.
* Even a later authentic structural output match remains `DRAFT_HARD_HOLD`, no human medical/food/emergency/child-privacy safety certification, browser accessibility certification, release, or commercial success.
* If source checkout or built exports are missing, the new gate deliberately exits **2** and reports `WORDPRESS_EXPORT_CUSTODY_FAILURE_HARD_HOLD`. No WordPress writes, paid calls, public routes or publishing occur.

## Conversion acceptance (one audience and one *potential* offer)

Audience hypothesis: family emergency-contact/reunification social search intent. **Grok/Praxxis must verify** existing published media `asset_id`, date, spoken hook, rights, public permalink, signed-out/mobile landing destination and campaign parameters. Only the already-authentic free, ungated Preparedness Archive can be considered as a landing destination; Article #15 and optional **free** Tool #104 remain emergency, child-privacy, print and qualified-source HOLD. The retired water guide is excluded. No authenticated rights-cleared, payable, deliverable FV-owned Preparedness toolkit SKU has been shown; therefore **NO PAID CTA** or product-status change. Do not label links/leads/clicks as sales.

Offer → step → blocker → experiment → evidence → owner:
1. **Verified existing owned toolkit → merchant checkout → payable SKU/rights/delivery/refunds absent → privately authenticate actual SKU, settlement and support → NO PASS / no paid order evidence → Founder + Commerce.**
2. **Published Grok reunion/contact asset → free Archive route → asset_id/message/rights/destination unverified → independently compare permalink and mobile signed-out CTA before any campaign mapping → HOLD → Grok/Praxxis.**
3. **Free Article #15 → optional free printable #104 → emergency/child-privacy/printing and source reviews pending → private-only CTA/UX inspection → HOLD → Preparedness/QD.**
4. **Qualified sessions → genuine paid settled order → source attribution, merchant receipts, fees and refunds missing → reconcile 7/30-day cohorts and show net revenue per 1,000 verified human sessions only from actual confirmed transactions → NOT COMPUTABLE → Claude/Commerce.**

All findings should be posted to #136; revenue blockers cross-referenced to #820. No CMS/navigation, analytics script, email, public assets, merchant/affiliate activation, spending, draft merge, or false QD PASS.