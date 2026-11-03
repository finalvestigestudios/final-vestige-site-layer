# Final Vestige Mind R101 — Independent Evidence & Zen12 Presell Review Pack

**Date:** 3 November 2026. **RELEASE STATUS: HARD HOLD / DRAFT ONLY.**  
**Ownership:** Mind & Perception investigation/editorial + exact-SKU Inspire3 presell landing pages and compliance measurement. **Excluded:** homepage PR #49, art-owner Issue #150, canonical hub PR #172, Dispatch newsletter drafts Issue #174, live WordPress CMS/settings/menus, Jetpack subscriptions/welcome email, affiliate activation and deployments.

## What's genuinely new

1. **`investigation.md`** — original approximately 2,050-word scholarly investigation of the rubber-hand illusion, *The Hand That Wasn't Yours*. It explicitly presents Botvinick & Cohen 1998, Rohde et al 2011, Lush 2020, Slater & Ehrsson 2022, Tsuji & Imaizumi 2024, with a bounded Puységur historical analogy and no commercial blocks.
2. **`zen12-guide.md`** — original approximately 1,780-word independent buyer guide addressing precisely the public `/hnp` offer and `/getstarted` full-course checkout. It distinguishes seller-formatted six- and twelve-level SKUs from the unsubstantiated twelve-minutes-equals-one-hour result, reviews independent binaural-entrainment evidence, privacy/refund terms, and a free three-occasion exercise. It does not claim a purchase, product trial, commission or price.
3. **`pilot-A-text-only.blocks.html`** — original fully authored ~1,000-word accessible independent text guide in a responsive design, with disabled CTA and prospective commission disclosure adjacent.
4. **`pilot-B-film-concept.blocks.html`** — **identical factual/consumer guidance** with original 40s video treatment, poster rendered as CSS, six-part transcript, no fake video player. A genuine MP4 has been produced *offline* but is not hosted or embedded. A/B difference is isolated to the optional video module.
5. **`film-storyboard.md`, `film-40s.vtt`, `render_film.py`** — original six-scene, 40.000s silent film concept, continuously timed subtitles and executable first-party renderer. Actual MP4 generated offline in this sprint: 540×960, H.264, 12fps, 480 frames, 77,832 bytes. SHA-256 `f4ed13c8c0748852689f7c00aae13031ad12f506b18d97930f38251b52fa49be`. Executed Python source matched GitHub blob SHA `b3ee855c94d0b88bb54a3c4383974954d0b48dd9`. Images/video not hosted or attached to WordPress.
6. **`mind-hub-preview.blocks.html`** — design-only noncanonical four-stream /mind/ hub referencing only existing established public routes, unlaunched guides described as unpublished. It **does not supersede PR #172**.
7. **`claims-and-sources.json`** — **19 factual source records, 36 claim/permission decisions, 35 closed release gates**, explicit null affiliate link, with account approval and purchaser-data exclusion unsatisfied.
8. **`synthetic-attribution.mjs`, `attribution.test.mjs`, `prototype.test.mjs`** — local-only whitelisted-category measurement demonstrator; rejects raw URLs/identifiers, disallows live events and suppresses all synthetic aggregate cells below 20. Includes seven native Node test blocks + eight static HTML/claims checks. No live analytics.

## Verified primary research and seller sources

**Research:** https://doi.org/10.1038/35784 ; https://doi.org/10.1371/journal.pone.0021659 ; https://pubmed.ncbi.nlm.nih.gov/24168532/ ; https://doi.org/10.1525/collabra.325 ; https://doi.org/10.3389/fnhum.2022.834492 ; https://doi.org/10.1525/collabra.116190 ; https://pubmed.ncbi.nlm.nih.gov/37205669/ .

**Exact merchant + permissions:** https://inspire3.com/ ; https://zen12.com/hnp ; https://zen12.com/getstarted ; https://inspire3.com/privacy/ ; https://inspire3.com/terms/ ; https://affiliates.inspire3.com/ . Public affiliate marketing is **not named Final Vestige acceptance or seller-approved creatives**. Merchant TOS restrict use of copyrighted assets without permission, so this pack creates entirely original film art and copy.

**Regulators:** https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

**Established Final Vestige bridges from Issue #171:** https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; https://finalvestige.com/focus/ . During R101 the general web tool failed to retrieve these live site routes; don't claim they were freshly validated. Existing 61-post count is **historical baseline**, not freshly recounted.

## A vs B: pre-registered conversion hypothesis (NOT an outcome)

**Question:** Does optional 40s, first-party educational film make a scientifically cautious offer guide easier to understand without damaging trust or performance? It is **not assumed to convert better**. A and B must have identical research/consumer claims, pricing treatment, source links, near-CTA disclosure and position of the genuinely disabled purchasing control. The only isolated B treatment is the optional, no-autoplay poster/transcript/film.

**Before any test with real readers:** affiliate approval, data minimization/consent where necessary, merchant PII exclusion, named product/channel authorization, disclosure audit, founder publication approval, Site QA accessibility review and independent performance QA. No live A/B assignment or network events now. Use only high-level aggregate, consented site events if legally and technically authorized; no user IDs, email, IP, query strings, raw referrer or affiliate order data.

**Potential high-level outcomes (future only):** reader comprehension measured without forced signup; percentage who locate primary research; % who select free Focus path; aggregate disclosed offer-interest clicks; page-experience indicators such as LCP, CWV, 360px layout, reduced-motion, caption availability. No claim that an outbound click is a sale. Compare under equivalent acquisition/source/channel distributions, sufficient sample sizes, preregistered decision rule, and control for seasonality. Do not provide percentage conversion uplift before observed data.

**Guardrails:** B film opt-in, `preload=none`, poster, synchronized caption track and visible transcript; no JS required to read guide; no external media or trackers. Small HTML footprint; future media load after user action only. No video widget may be shown as playable until hosting is valid.

## Tests

Run from repository root with Node 18 or newer:

```sh
node --test mind/review-r101-rubber-hand-zen12/attribution.test.mjs mind/review-r101-rubber-hand-zen12/prototype.test.mjs
```

Static HTML/claims files should be checked against the exact PR commit. **V8 policy checks were executed on fetched committed-source files in the creation run**. Native Node runner and hosted Actions are not yet certified; do not claim those ran without real logs.

Once media is approved, regenerate the film on a host with Pillow and FFmpeg using:

```sh
python mind/review-r101-rubber-hand-zen12/render_film.py
```

The renderer uses an installed DejaVu font path; deployment machines may require a local font-path adjustment (never distribute fonts). **Do not share software font files as artifacts.** The locally produced MP4 and poster files are sandbox review assets, not web-hosted.

## Internal-link and navigation plan

- Existing published Puységur archive → after approved publishing, add **one historically framed evidence-methods link** to the independent rubber-hand investigation. Do not suggest the archival magnetizers discovered the phenomenon.
- New rubber-hand investigation → Contextual “read next” to published Change Blindness when that exact canonical slug is revalidated; no product pitch embedded in investigation.
- New /mind/ curated hub (subject to PR #172 owner) → prominently house attention, history, practice, tools-under-review independently, without modifying the existing six categories.
- `/focus/` remains the only free Focus opt-in; no second form, list, lead magnet or duplicate welcome email.
- TikTok organic intro → investigation first → /mind/ or the free Focus resource; only then optional consumer guide. Commercial TikTok links must remain withheld pending product/channel license.
- One restrained homepage portal, if ever desired, is exclusively for homepage art lead Issue #150 review and **must not** be added by this branch. PR #49 frozen.

## Outstanding independent permissions and release gates

**Unresolved:** Final Vestige-specific affiliate acceptance and Zen12 tracking URL; product-approved SITE, TikTok, email promotions; merchant creatives or written permission; partner reporting that does not reveal buyer name/email/purchases (current published privacy policy permits it); verification of current SKU checkout/refund and merchant redirects; independent medical/psychological implied-claim check; staging Gutenberg sanitizer and link test; keyboard, touch, screen reader, actual 360/390/768/1440/1920 layout, reduced-motion/contrast AA tests; actual hosted MP4/picture/VTT caption sync; Lighthouse low-bandwidth and LCP; brand/site QA review; explicit founder publishing authorization.

The public Inspire3 affiliate portal's headline figures and the checkout's current visible price/timer must **not** be used as verified affiliate terms, commissions or durable consumer prices. No affiliate or commerce activation under this PR. No editing of Dispatch Issue #174's issue drafts. No live CMS updates, marketing sends, navigation changes, merges or deploys.

**QA handoffs:** Issues #126 Site QA, #150 homepage art, #174 Dispatch. Record exact PR/SHA and actual executed results in Issue #171 before treating this deliverable as complete.
