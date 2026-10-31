# Mind R13 execution record — independently reread source files

**Run date:** 2026-10-30 PT / 2026-10-31 UTC. **Branch:** `feature/mind-stroop-conflict-evidence-20261030-r13`. All files were read through authenticated GitHub connector at this branch; exact commit SHA and PR URL should be logged in Issue #171 after PR creation. No real website writes.

## Source readback and test procedure

After source, markup, ledger, strategy, script and README were written, all seven files were retrieved from GitHub by path and branch. The content of `qa.cjs` was compiled and executed using a V8 JavaScript evaluator with `module.exports.audit` on those same GitHub source readbacks. This is **actual execution** of the committed audit function; it is **not** a Node CLI execution on a checkout and not a hosted GitHub Actions run.

**Result: 76/76 checks passed.** These cover a single h1 and article landmark, all 15 source anchors and citations, no scripts/forms/third-party media, no unverified seller checkout links, explicit conditional commercial disclosure, off-by-default partner/measurement statuses, no invented product claims, meaningful free alternatives, mobile/reduced-motion/forced-colors source provisions, and seven calculated text-on-background color contrasts meeting 4.5:1 minimum.

**Adversarial mutation run: 17/17 detected.** The checks rejected purposeful contamination with active seller checkout, executable script, off-site iframe, new email form, deleted commercial-disclosure label, fake buy button, broken source anchor, disabled Focus CTA, missing focus CSS, missing reduced motion, fabricated clinical efficacy, false partner acceptance, invented approved affiliate URL, invented email permission, promoted unsupported meditation-hour equivalence, enabled measurement, and a claim that the concept-only film was rendered. Changes were held in memory for negative tests and **not** committed.

**Exact file blob SHA readbacks** (after fixing disclosure/source anchor guards):
- `ARTICLE.md` — `16878ea6da2117ab390c3b4849b06a7db480ff4e`
- `wordpress-draft.html` — `3623d45b24f16070ffec0a23ae6e2a970c91ae58`
- `claim-source-matrix.json` — `9176aef18baa43b85ca1f281643d661d5db13395`
- `OFFER_EXPERIMENT_AND_NAV.md` — `b258b6f44df0679245f488d5b2bdcaebc253ea72`
- `SHORT_VIDEO_CONCEPT.md` — `cc7f7784362650fbae312c4923ede4b8481e19fe`
- `README.md` — `d3c7a9802456a329a8860f2f41e6db399afa80da`
- `qa.cjs` — `4b7cd7f33cb241a738cfe0eda60ed1789e337f46`

## Separate media-provenance recheck (PR #229, not committed in this R13 PR)

The locally accessible prior founder review bundle `FV_Zen12_Evidence_Film_Review_2026-10-30.zip` contains portrait and widescreen 40-second silent files, original posters, `captions.vtt`, transcript, source scripts and offline screenshot proof. Verified with `ffprobe` in this run:

- Portrait `final-vestige-zen12-evidence-40s-portrait.mp4`: H264, 540×960, 15 fps, **40.000000 seconds**, **155,763 bytes**, SHA-256 `c4cb33fef60dfa773e65a46b9167c0581e58cf07f09c42b744f90c60af48ebbc`.
- Widescreen `final-vestige-zen12-evidence-40s.mp4`: H264, 960×540, 15 fps, **40.000000 seconds**, **149,680 bytes**, SHA-256 `eb4a3f7e7d95ce5a6ff1ba08c83e66a4f7cc94cb1e3784bd51a330650c41ab00`.
- Source bundle `captions.vtt`: 5 cues spanning 00:00–00:40 and source-bounded statements about the seller-described Zen12 formats; `transcript.md`: present and readable. This inspection does **not** establish caption synchronization in an actual browser or public CDN hosting.

No media binary, media embed, checkout or tracking destination is added to this R13 branch.

## WordPress-first factual read

Authenticated read-only WordPress pages inventory showed **61 published investigation posts**, published `Puységur’s Animal Magnetism Files` page ID 1377 and `Free Seven Day Focus Fieldbook` page ID 1579. Palette matched verified live design tokens (#090A0A, #F4EFE6, #B8955E). The Focus rendered content returned by REST represented a Jetpack subscription area as a self-link anchor instead of an email input in the retrieved representation; **this is not proof of a public browser failure**, but warrants an explicit logged-out Focus subscription flow test before driving traffic. No change to its existing Jetpack configuration is authorized.

## Hard release blockers

Independent editorial check against sources and health-advertising implications; exact WordPress staging and sanitizer check; mobile screenshot / keyboard / 200–400% zoom / assistive technology / Safari; actual media caption and no-JS QA for the film variant; full Lighthouse/transfer analysis; hosted CI or complete exact-checkout Node; current merchant feature/refund terms; private Inspire3 account acceptance with exact SKU-approved tracked link, email and creative permissions; founder-governed release approval. Commercial and WordPress release status remain **HOLD**.

Source note: vendor affiliate landing https://affiliates.inspire3.com/ is public recruitment copy, **not** proof of account acceptance or the specific payout terms to this publisher. No payout, current product price, medical benefit, wealth benefit, campaign result or personal customer experience has been claimed.

**No production CMS, homepage PR #49, owner #150, Mind hub #172, prior Zen12 film #229, Jetpack list, Dispatch #174 or site settings were modified.**
