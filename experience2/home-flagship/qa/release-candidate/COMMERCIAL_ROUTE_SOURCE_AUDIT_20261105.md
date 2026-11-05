# Final Vestige homepage: first-party commercial route admission — P0 (HOLD)

**Observed:** November 5, 2026 UTC, via authorized read-only WordPress site 256784396. **No production writes, affiliate activation, merchant access, signup submissions or new scripts.** Child of Issue #150; commercial coordination Issue #820 and charter #818. Frozen PR #49 untouched. Separate from Apollo #158, Mind/Affiliate #171, Grok/Praxxis TASK-008, and Claude's production attribution work.

## An actual conversion blocker, not another decorative prototype

Source-verified WordPress pages:

| Page | Modified (WordPress API) | Read-only source observation |
|---|---|---|
| Published homepage Page 6 | 2026-11-04T14:39:24 | 4 direct `/focus/` links, 1 `/dispatch/`, **0** links to `/collection/` or Payhip inside page body. Its Assembler global header separately has Editions (`/collection/`) and Free Ebook (`/focus/`). This is not a claim the site has no commercial paths. |
| The Collection Page 78 | 2026-10-29T15:37:38 | 4 `/focus/` links, 2 Awin/Suunto outbound affiliate links to the same target, a nearby commission disclosure and link to full affiliate disclosure; **0** direct owned-product merchant destinations. |
| Focus Page 1579 | 2026-11-03T14:36:15 | Fieldbook offer text and Jetpack subscription markup exist. The previous owner test reported successful confirm+welcome emails, but that does not prove attributable or current new paid sales. |

This is a **specific first-party monetization gap at the existing public storefront**: no owned paid item is presented for purchase on `/collection/`. There may be products on external Payhip not reflected here. No merchant catalog, prices, rights, availability or actual paid order can be verified from this page's source. The Awin outbound link is a possible affiliate referral, not an affiliate sale, and its presence cannot be counted as revenue.

## Immediate conversion route (single high-intent test)

**Audience:** History/evidence readers arriving from a topic-matched Grok social investigation. **Current destination:** the relevant article or homepage historical chapter; use the existing Fieldbook CTA only when relevant and preserve the seven archival chapters, 72 Margins, evidence links and Jetpack. **Offer candidate:** one pre-existing, rights-cleared paid Final Vestige evidence dossier or educational pack, **only after** Claude/owner validates Payhip product status, ownership/licensing, refund policy, realistic price and working checkout. Do not substitute invented SKU, prices, scarcity or claims. If no approved offer qualifies, run a lead-only journey and explicitly label it that way.

**Hypothesis:** A contextual, named, independently reviewed paid dossier link on the relevant historical page plus `/collection/` can produce a greater **merchant-confirmed** paid order rate among qualified campaign visitors than free Fieldbook-only routing, without reducing trust or verified lead capture. This is a future experiment proposal, not a result. Do not modify production without separate founder release approval.

**Homepage art direction:** Keep the monumental Franklin hero and editorial evidence as the first screen. A paid-offer path must be contextual, not another sticky popup or an interruption above the historical proof. Existing FREE EBOOK header and mobile strip should be hit-tested at 320/390/1279/1280px before any duplication. No change to site branding or seven chapters proposed here.

## Gate / evidence / owners

| Offer | Funnel step | Blocker | Proposed change | Evidence and acceptance | Owner |
|---|---|---|---|---|---|
| 52-page Fieldbook (free) | Hero/history → `/focus/` → confirmed lead | Form source does not prove actual delivery or attribution | Keep current offer; check actual CTA visibility, consent, confirmation and welcome in approved QA | Current links + form markup **source PASS**; live anonymous mobile, deliverability and conversion metrics **UNVERIFIED** | Homepage + Claude |
| Verified, rights-cleared FV paid dossier **TBD** | Relevant investigation → Collection/product → paid checkout | No owned paid product link in Collection; merchant and rights unavailable | Verify one existing Payhip SKU, then stage a single nonintrusive offer path | **HOLD** until real merchant product ID, rights review, working checkout, terms, explicit release approval | Founder / Claude / product studio |
| Suunto Awin compass | Contextual external referral | Referral is not independently confirmed sale | Preserve adjacent affiliate disclosure and editorial independence | Link/disclosure **SOURCE VERIFIED**; merchant acceptance, paid commissions **UNVERIFIED** | Affiliate lane |

**Measurement:** Grok immutable `asset_id` in `utm_content`, source/platform, campaign → qualified-human landing session → relevant CTA click → confirmed lead (if observable) → merchant-confirmed order → refunds/fees → net revenue. Report 7/30-day small-sample warnings and net revenue per 1,000 qualified human sessions only when both trustworthy human-session denominators and realized net revenue exist. Do not instrument here; Issue #820 is Claude's analytics implementation source of truth.

## Executable admission

Run `node --test test_revenue_path_gate.mjs` (14 passing native tests, including negative controls) and `node revenue_path_gate.mjs <public-home.html> <public-collection.html> <public-focus.html>` on public-only exported HTML. The CLI intentionally exits with code 2 when the Collection page lacks an owned checkout destination. Presence of a Payhip link changes the result only to `MERCHANT_CHECK_REQUIRED`, never `PAID_SALE_VERIFIED`. No subscriber information, cookies, API keys or secret-laden content should be supplied.

**Not measured:** Actual anonymous Chromium, axe/WCAG 2.2 AA, WordPress Playground exact-source, physical 200% zoom, responsive image transfers, Lighthouse/CWV, verified merchant orders or net revenue. Previous real WordPress staging PR #637 was a different SHA; it cannot certify this current candidate. GitHub Actions may still fail without runner steps.

**Release:** HOLD. This audit is read-only and can be reviewed independently; no production CMS write, plugin install, deployment, paid activation, affiliate URL change, social post or subscriber action is authorized by it.
