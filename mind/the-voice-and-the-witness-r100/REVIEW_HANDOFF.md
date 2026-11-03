# R100 — Mind & Perception release-review handoff (2026-11-03)

**RELEASE: HARD HOLD · DRAFT ONLY · NO LIVE CMS CHANGES · NO AFFILIATE ACTIVATION.** This self-contained directory is isolated from the public homepage PR #49, the authoritative Mind Archive PR #172, Issue #150, and Dispatch newsletter work Issue #174. All repository files in this PR are new; do not merge/publish without explicit founder release approval.

## Why this milestone is different
The previous run produced a Puységur investigation and a Total Focus product review. This run opens a distinct documented historical path: from Puységur and the 1784 investigation, via Braid's 1843 book, to Émile Coué's 1922 autosuggestion movement and peer-reviewed studies distinguishing *self-directed* self-hypnosis from *passive audio*. It gives a reader genuine independent value rather than writing another conversion claim on top of an already-unverified offer. The investigation has no commercial block.

**Deliverables:**
- `investigation.md` — **2,100-word original research investigation**, *The Voice in Your Head Was Not a Hypnotist*, eight supporting documentary/scholarly references, a no-purchase observation and a bounded relationship to the published Puységur archive.
- `zen12-source-guide.md` — **1,140-word independent buying guide** based on precise merchant /hnp sales and /getstarted checkout page, active privacy policy, independent binaural-beat review, FTC rules, and a no-purchase practice exercise. Never says Final Vestige tested the program.
- `pilot-A-text-only.blocks.html` + `pilot-B-video-guide.blocks.html` — original source-controlled Gutenberg **HTML-block prototypes**, with exactly equal evidence-guide markup. B alone adds accessible original 40-second storyboard/poster/transcript. There is **no actual video element or false playback promise in HTML**, until hosting/caption QA. CSS is scoped and no-JS-readable. No live merchant URLs; proper prospective disclosure directly before a native disabled button.
- `film-40s.vtt` — six closed-caption cues covering 00:00–00:40. No soundtrack, no external media, no forced playback.
- `render_film.py` — original reproducible **Pillow + FFmpeg** renderer. Locally executed: 40.000s, H.264, 540×960, 12fps, 480 frames, **SHA-256 of rendered MP4 `5befd76440d3b18a3a789d328187a122064b8cae693218c95bcc989dcfec0828`**. Renderer Git blob SHA **`9ffe4dc7493f8490db1b8d3d969e4ee00ee8963d`** exactly matched local source file. Original MP4, poster PNG, contact sheet and offline ZIP were created in the run sandbox, not hosted on WordPress or uploaded to GitHub.
- `mind-hub-preview.blocks.html` — noncanonical four-stream /mind/ Gutenberg HTML-block design **for comparison only**, NOT a replacement for draft PR #172; only verified live pages are clickable.
- `claims-and-sources.json` — **19 source records, 40 explicit claim/permission judgments, 25 fail-closed release gates**; `affiliate_url=null`.
- `synthetic-rollup.mjs` — **synthetic-only** attribution counter with strict three-field categorical allowlist, >=20-reporting threshold and PII-key rejection. No script import in page; no collected real events.
- `tests.mjs` — reproducible native Node test plan. Run from this directory: `node --test tests.mjs`.

## Executed local/source-integrity evidence
- Exact authenticated GitHub readback of each of 11 initial sources PLUS the Python renderer (12 total files prior to this handoff) confirmed their hashes and sizes.
- **8/8 pre-commit A/B, disclosure and static-security checks passed**.
- **31/31 manually executed V8 checks passed** against committed synthetic-rollup.mjs, including 13 rejected extraneous fields, invalid categories, >=20 suppression, and release-gate verification.
- Exact-blob re-read: A/B shared guide matches byte-for-byte after removal of B film aside; both native CTAs disabled; zero clickable merchant URLs; zero script, form, autoplay, iframe, active media or analytics; six closed VTT cue intervals. Renderer Git blob matched the local script.
- Native local Python/FFmpeg output inspected via a six-panel contact sheet; media verified at 40.000s/480 frames/540×960/H.264, offline ZIP integrity passed.
- **Not executed/NOT claimed:** native Node test suite, hosted CI green for this PR, HTML in actual WordPress with its sanitizer, production mobile/keyboard/contrast/full accessibility QA, staged playable video and caption synchronization, Lighthouse/CWV and any real A/B conversion study.

## First-party source audit (2026-11-03)
- Merchant brand: https://inspire3.com/ .
- **Exact Zen12 offer:** https://zen12.com/hnp .
- Full Zen12 checkout: https://zen12.com/getstarted .
- Merchant research/sales assertions: https://zen12.com/research .
- Privacy, including potential buyer identification to affiliates: https://inspire3.com/privacy/ .
- Generic partner portal, **NOT founder account approval**: https://affiliates.inspire3.com/ .
- FTC endorsement disclosure FAQ: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking .
- FTC product health claim substantiation: https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .
- Primary Coué (1922): https://www.gutenberg.org/ebooks/27203 ; primary Braid bibliographic record: https://openlibrary.org/books/OL7187745M/Neurypnology ; theory review https://pubmed.ncbi.nlm.nih.gov/39032268/ ; self-hypnosis RCT review https://eprints.bournemouth.ac.uk/31277/ ; binaural EEG review https://pubmed.ncbi.nlm.nih.gov/37205669/ .
- Read-only live WordPress page 1377, Puységur; live 1579, Seven Day Focus Fieldbook. Search for published `self-hypnosis` posts found no exact match. Issue #171 historical 61 published post baseline is **not** a newly confirmed count for the entire site.
- Official partner swipe/creatives are not available from the unauthenticated portal and **no reuse rights are presumed**.

## Practical A/B evaluation design (not active)
1. Variant A and B contain identical independent guide text. B adds a 40-second original optional video **only after first-party approved hosting/captions**, and the HTML must gain an accessible user-initiated player or poster+button progressive enhancement; no autoplay.
2. Do not assign visitors, plant cookies, or collect outbound events yet. The current JavaScript source is an offline synthetic prototype. If approved later, prefer existing privacy-safe aggregate analytics, source/variant/action categories only, no IP/email/device identifiers, timestamps, raw URLs, fingerprinting, querystrings or inferred buyer records.
3. Pre-register primary measure (approved outbound offer-button interest per *eligible guide view*, with explicit denominator), guardrails (readability, page performance, disclosure comprehension and bounce), a valid sample-size plan, and a stop rule. Do not claim video uplift without sufficient data. Small groups under twenty observations must be suppressed.
4. The test only makes sense after identical verified affiliate links and rights have been approved for both versions. No conversion tracking now.

## Navigation and ownership
**TikTok or organic query** → source-grounded investigation → **optional existing Focus Fieldbook** or plain /mind/ navigation → independent product guide → **only then** a disclosed merchant link after partner authorization. Do not gate knowledge behind email signup. Do not change existing Jetpack list/welcome, publish a WordPress draft, modify navigation, overwrite homepage PR #49 or convert /mind/ PR #172. Coordinate with homepage art lead Issue #150, Site QA Issue #126 and Dispatch #174. Newsletter Issues 03/05 remain merchant-gated and this run makes no changes to them.

## Precise release blockers
- Founder-specific written Inspire3 affiliate acceptance, actual authorized link, channel rights website/TikTok/email, rights to any partner creative, confirmed partner reporting terms and **written exclusion of purchaser names/emails/purchased items**.
- Reverification of actual price/checkout conditions/refund process at activation, independent legal/scientific claim review, and effective FTC near-link disclosure after activation.
- Human editorial QA and author signoff, WordPress HTML-block sanitizer behavior, mobile views 360/390/768/1440/1920, keyboard focus, WCAG AA contrast, screen readers, actual first-party media hosting/captions, performance budget and privacy review.
- Founder publication and deployment approval **separate from approval to prepare this draft**.

**No WordPress writes, no new subscriptions/list, no dispatch edits, no deployment, no tracking, no media upload, no affiliate activation.**
