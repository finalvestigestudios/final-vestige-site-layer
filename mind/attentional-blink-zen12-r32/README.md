# Mind & Perception R32 — attentional blink + Zen12 evidence-first comparison

**State:** Completely **UNPUBLISHED**, isolated draft review only. Nothing installed, merged or deployed. Merchant controls, instrumentation and email sends **OFF**. Main branch, PR #49, Issue #150 and Mind archive PR #172 remain unchanged.

## What is new and why
Instead of another paraphrased perception illusion, the investigation follows the *actual procedure*, 2020 close replication and 2007 intensive-meditation finding of the attentional blink—while resisting the tempting but invalid inference that this evidence proves a 12-minute Zen12 proprietary recording improves attention. The buyer's guide is independently useful even when the merchant is not approved.

- `INVESTIGATION.md` — original 2,488-word sourced narrative, historical bridge to Puységur, limitations and completely free non-diagnostic exercise. **No affiliate promotion**.
- `INVESTIGATION-WP-DRAFT.html` — styled, scoped, static, no-JS Gutenberg Custom HTML conversion.
- `ZEN12-INDEPENDENT-GUIDE.md` — original 1,850-word product-specific independent buyer's guide: actual seller packages, four advertised styles, concrete objections, free 12-minute routine, alternative choices and source trail.
- `ZEN12-WP-VARIANT-A.html`, `ZEN12-WP-VARIANT-B.html` — same exact source-derived editorial body, B alone adds an original 40-second **optional offline-film** presentation with inline accessible static SVG and full transcript. A/B comparison remains **unexecuted**. Both have conditional near-button affiliate disclosure and a **disabled, link-free purchase button**.
- `render.cjs` — deterministic local source-to-HTML converter (no WordPress credentials, requests or production side effects). Reproduce: `node render.cjs investigation draft-investigation.html`, `node render.cjs A draft-a.html`, `node render.cjs B draft-b.html`.
- `HUB-WP-DRAFT.html` — alternative draft `/mind/` hub using real published source links, preserving owner PR #172 and six historical category architecture.
- `EVIDENCE-MATRIX.csv` + `SOURCES.md` — **60 claim/permission decisions** with **18 source IDs/URLs** dated 2026-10-31, differentiated as independently supported, seller-described, not supported, or unverified authorization.
- `render_short.py` + `FILM.vtt` + `FILM-PROTOCOL.md` — **genuinely rendered original 40.000-second silent H.264 short film**, 540×960, 12fps, 84,220 bytes; SHA-256 `31b2b2c48b574192ff6b1e394018c836aa86bfc92742c10b7bab4c7caec14181`. Actual video and generated PNG live only in the working conversation sandbox; source code and exact caption/transcript cues are in this PR. No first-party hosting, no live player, no autoplay. Two offline frames manually viewed.
- `AB-NAV-MEASUREMENT-PLAN.md` — internal-link/TikTok route, preregistered hypothesis, no email funnel duplication and publication consent conditions.
- `privacy-off.cjs` — synthetic-only strict categorical aggregator, hard-disabled; no network, PII, cookies, visitor IDs or raw referrers. k=10 suppression; **not deployed analytics**.
- `qa.cjs` — reproducible source-level guard and harmful-mutation tests.

## Current verification (actual remote GitHub committed readback, R32)
- Re-fetched **15/15** initial committed files (all docs/scripts/HTML excluding this README) from the branch.
- Executed committed `qa.cjs` as JavaScript in isolated V8 against **exact GitHub file readbacks**: **76/76 source-quality assertions passed**; **10/10 targeted unsafe mutations correctly detected**. A/B parity checked at generated HTML byte level after excluding only B's optional film block.
- Executed exact committed `privacy-off.cjs` self-test against readback: **29/29 privacy/schema tests passed; ENABLED=false**.
- Independently ran ffprobe on actual local MP4: H.264 540×960, 12/1fps, exactly 40 seconds, 84,220 bytes. SHA-256 calculated, frames 10s and 30s inspected. **MP4 not uploaded or hosted**.
- Tests were performed in a mocked readback-backed JS environment, **not** a native repository checkout or hosted CI. WordPress staging, real browser accessibility, actual lighthouse/CWV, final poster/track syncing in a hosted player and real conversion outcomes **remain UNVERIFIED**.

Reproduce on native checkout: `node mind/attentional-blink-zen12-r32/qa.cjs`; `node mind/attentional-blink-zen12-r32/privacy-off.cjs`. Re-render WordPress candidates with `render.cjs` as above. Film: `python render_short.py --out zen12-attention-40s.mp4`. No external paid services.

## Review and hard-hold matrix
**Seller and official offer reviewed:** https://inspire3.com/ ; https://zen12.com/ ; https://zen12.com/about ; https://zen12.com/getstarted ; public affiliate https://affiliates.inspire3.com/ (signup page is not partner acceptance). Seller claims Beginner first 6/24, Premium all 12/48, Advanced final 6/24; no stable current price or commission asserted. No merchant swipe creative copied. No invented personal trial, outcome, medical or wealth promise. Distinguish seller statements about one-hour meditation equivalence and brainwave entrainment from independently corroborated product effects.

**Science reviewed:** https://pubmed.ncbi.nlm.nih.gov/1500880/ ; https://link.springer.com/article/10.3758/s13428-020-01457-6 ; https://journals.sagepub.com/doi/10.1111/j.1467-9280.2006.01730.x ; https://pubmed.ncbi.nlm.nih.gov/16028578/ ; https://pubmed.ncbi.nlm.nih.gov/17488185/ ; https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety .

**FTC:** https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

**Release blockers:** signed account-specific Inspire3 acceptance; approved exact tier/SKU earning URL and site/TikTok/email promotional permissions + creative licenses; current and buyer-region-specific refund/checkout/contact/phone/privacy terms; independent claims/legal review; native checkout and hosted CI; Site QA #126 WCAG 2.2 AA and 360/390/768/1440/1920 browser QA, no-JS/reduced motion/keyboard/screenreader and Lighthouse; actual approved first-party film-hosting and accurate caption sync for B; homepage art lead Issue #150 review without touching flagship PR #49; Dispatch #174 email products #03/#05 HOLD_MERCHANT and all drafts HOLD_UNSENT. Explicit founder publication, navigation, analytics, link activation and merge/deploy approval is essential.

**Invariants:** No WordPress content/menu/settings/media write, no Jetpack or Focus signup change, no new list, no emails, no merchant contact, no real visitor tracking, no live affiliate earning URL, no deploy.
