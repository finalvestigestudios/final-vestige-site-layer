# Mind & Affiliate Studio R71 — Ideomotor / Zen12 Draft Pilot
**Status:** UNPUBLISHED / HARD HOLD. Entire change confined to this directory. No live WordPress mutation, deployment, tracking, popup, Jetpack setting, newsletter edit or homepage PR #49 edit. Canonical Mind hub PR #172 remains authoritative; this hub candidate is noncanonical.

## Editorial asset
- `investigation.md`: original ~1,942-word *The Pendulum That Answered Without Knowing*. It treats historical ideomotor theories and three research papers with distinctions between movement, mechanism, and knowledge. It explicitly links only to the **already live** Puységur source archive. No seller mention in the conclusion or affiliate links.
- `zen12-guide-core.html`: evidence-checked independent buyer guide to **Zen12**, not Hypnosis Live Total Focus. Seller official pages were checked on 2026-11-02 and kept as plain-text provenance, not active commerce links. Includes practical no-purchase three-occasion format preference audit, privacy/refund objections and scientific boundaries. Not a first-person product test.
- `zen12-a-text.blocks.html` and `zen12-b-film.blocks.html`: substantive guide core identical. B inserts ONLY an optional original 40-second video concept, static accessible illustrated poster, six-cue transcript, and clear withholding of playback until first-party media is authorized and hosted. Neither page includes a working checkout, popup, form, script, tracker, embedded video or autoplay. Both have near-button prospective affiliate disclosure and genuine HTML `disabled` property.
- `mind-hub-noncanonical.blocks.html`: four-stream Gutenberg draft, no fictitious published URLs or second signup form.
- `film-poster.svg`, `captions.vtt`, and `render_film.py`: original illustrated poster, accessible caption source and **reproducible executable Python/Pillow + FFmpeg renderer**. Separately rendered the actual 40.000-second H.264 MP4 for **offline review only**, 540×960, 12 fps, 480 frames, 591,514 bytes; SHA256 `b383c41a9cccd9d6c60eaca7e6d10fbff7d20d2c7853a8548f100226be0a7097`. The renderer's Git blob is `cbd7d0833ed2dfb3d811029a616f299efc44179a`, exactly matching the local renderer used. Offline `review.html` has native video controls, matching six-cue captions and a full no-JS transcript. ZIP integrity passed; ZIP SHA256 `fed6da8f50211c4d44fe4edc7f7e30d35a76b039e64279471f03b7d59cfb4fda`. The website Variant B remains a **nonplaying poster/transcript-only candidate until approved first-party media hosting, real browser caption-sync QA and founder release**. No MP4 binary has been committed or uploaded to WordPress.
- `claim-matrix.json`: 22 actually identified source URLs, line-item seller claims, unsupported outcomes, privacy, permissions and hard-release gates.
- `attribution.mjs`: disabled, no-network, no-PII synthetic-only aggregation proof. Must not import into public page or send real visitors anywhere.

## Research provenance (checked November 2, 2026)
Official Inspire3 catalog: https://inspire3.com/
Actual offer: https://zen12.com/hnp
About: https://zen12.com/about
Seller research: https://zen12.com/research
Checkout: https://zen12.com/getstarted
Privacy: https://inspire3.com/privacy/
Affiliate recruitment: https://affiliates.inspire3.com/ (NOT approval/terms)
Independent 2023 EEG review: https://doi.org/10.1371/journal.pone.0286023
NCCIH meditation: https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety
FTC endorsement: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
FTC objective health claims: https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
Exact Total Focus alternative: https://hypnosislive.com/mental-skills/total-focus (separate 33-minute product, NOT interchangeable).

**Commercial copy boundary:** Describe Zen12's durations, formats and inclusions only as *merchant-advertised*; never repeat 12min = 1h advanced meditation, guaranteed EEG entrainment, cognitive rewiring, health/wealth transformation, or advertiser testimonials as proven or typical. Current price/commission not carried into evergreen copy. One-year guarantee described only as seller's representation; no actual refund tested. Checkout mobile field and potential SMS/affiliate information sharing surfaced as reader objections.

## Organic / TikTok / internal-link plan
- 15-second teaser: "A pendulum can answer without knowing. The motion is real; what did it actually prove?" CTA should route to the published investigation only **after** separate editorial release.
- Article primary sources at end; article links to *already live* Puységur. No affiliate block attached to investigation conclusions.
- Mind archive candidate will route to perception experiments, suggestion history, existing Focus Fieldbook and independent tools review. Only Puységur and Focus routes currently confirmed live. No fake /mind/ or article URL.
- At the bottom of independently released guide only, the one already approved `/focus/` Fieldbook path is an optional independent alternative. It is **not** an email gate required to read the review.
- Homepage art lead Issue #150: suggest a single editorial-only "who moved the pendulum?" teaser after flagship release, but DO NOT modify the flagship home PR #49 or issue owner work.
- Site QA Issue #126: request independent exact-claim trace, HTML sanitizer/browser visual review, 360/390/768/1440/1920 widths, keyboard/VoiceOver/NVDA, reduced motion, high contrast and actual Core Web Vitals.
- Dispatch Issue #174: separate email copy and existing Jetpack excerpt-mode warning remain its owner's domain. No published Zen12 destination or approved EMAIL-channel permission exists. Do not inject guide into 03/05 newsletters, replace welcome message, or send tests.

## Text versus film pilot (test proposal, not conversion claim)
A = useful independently sourced text guide. B = same guide byte-identically plus optional 40s educational film **when first-party MP4/captions/media/consent/ownership are verified**. Compare qualified outbound *intent* in a consent-sensitive, aggregate-only deployment later, with predefined topic/variant/channel categories; never attribute purchases without authorized partner conversion data.
- No autoplay; `preload="none"`, `playsinline`, `controls` for any **future** first-party video. Visual title and full transcript available without JS/media, no decorative animation required.
- Prefer optional small poster + separate mp4; do not degrade LCP of the text-only page. Baseline actual metrics absent; A/B is an open hypothesis.
- A real experiment needs trustworthy randomized assignment, prespecified success metric, attribution and privacy policy review, reasonable sample, and a decision rule; do not claim lift merely from a rendering test.

## Executed verification
- 2026-11-02: 24 of 24 source-controlled `node:test` bodies replayed against exact fetched GitHub branch source through a V8/Node-compatible harness; NOT native Node or GitHub Actions. Initial transcript regex was too strict for a human-readable 35–40 second timestamp; corrected and rerun 24/24. Source and VTT assertions verified, no active offer checkout or network tracking.
- Local native FFprobe: MP4 H.264, 40.000 seconds, 540×960, 12/1 fps, 480 frames. All six film scenes sampled and visually inspected. ZIP archive integrity PASS. Browser/Lighthouse/native Node test run still unverified.

## Reproducible test contract
Run from this directory: `node --test ./tests.test.mjs`. No npm modules needed. Tests cover A/B substantive identity, true disabled button, disclosure proximity, absence of sales href or media/embed/scripts, no extra form, source integrity, evidence matrix, captions duration, disabled attribution, and suppression of synthetic cohorts under 20. **Passing tests do not prove WordPress sanitizer compatibility, WCAG AA, affiliate permission, customer consent, captions synchronization, performance, or improved conversion.**

## Release hard hold
Require all: named FV partner account acceptance; original affiliate channel/creative terms including TikTok and email; offer-specific authorized earning URL; written rights to any third-party creatives (this sprint uses none); current source/checkout/refund/privacy recheck; independently supported claims; first-party film MP4 and actual caption sync; QA + browser/CWV proof; separate explicit founder approval for publication; and separate authorization for any tracking. No edit of live CMS, nav, fieldbook, Jetpack, Dispatch, flagship homepage, agent-owned Issue #150, or PR #172 is authorized.
