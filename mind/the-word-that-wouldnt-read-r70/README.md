# Mind R70 — The Word That Wouldn't Read Itself / Zen12 Evidence Pilot

**Version:** November 2, 2026. **UNPUBLISHED / DRAFT / HARD RELEASE HOLD.** Only add files under this R70 directory. Founder permission to create drafts does not authorize production CMS edits, affiliate activation, trackable events, merge, newsletter sends or deployment.

## Research and editorial deliverables
- `investigation.md` — original ~2,000-word Stroop/hypnotic suggestion history and neuroscience investigation (Stroop 1935; Raz et al. 2002, 2005, 2006; Zahedi et al. 2024; Raturi et al. 2024). Original demonstration and strict interpretation boundary; the historical Puységur bridge preserves failures and consent issues. Scholarly claims tied to primary papers, no paid endorsement in conclusions.
- `guide-core.html` — original ~1,500-word Zen12 purchasing guide. Exact seller catalog+sales+about+research+checkout+terms+privacy pages checked on 2026-11-02. Features attributed; no promises about hour-equivalence, brainwave control, guaranteed focus, stress/health/wealth. Explicit mobile/SMS/affiliate sharing and refund-policy considerations. Free three-session listening-preference exercise.
- `zen12-guide-a.blocks.html` and `zen12-guide-b-video.blocks.html` — source-controlled, Gutenberg-compatible A/B candidates with **identical substantive core guide**. B adds original poster and complete timecoded transcript for optional 40-second educational film. Neither implies an unhosted player actually works. No JS, frames, forms, autoplay, checkout links, tracking, externally embedded media or fake urgency. Adjacent prospective commission disclosure and **native disabled** purchasing controls.
- `mind-collection-draft.blocks.html` — isolated noncanonical supplemental Mind hub visual/IA candidate. Do not overwrite canonical Mind hub draft PR #172. Actual site has six editorial categories and 61 published investigation posts; only already-published Puységur, Focus, standards and Explore routes link outward. Not live.
- `source-ledger.md` and `claim-matrix.json` — 48 enumerated evidence/claim/permission decisions; precise seller vs independent sources; release hold provenance and data-governance boundaries.
- `attribution.mjs` — disabled-by-default synthetic categorical aggregator; fixed vocabulary, no full referrer, URL, cookie, email, phone, IP, UA, storage, network calls, or sales inference. Threshold **20** for reported cohorts. This is code architecture only, not live analytics.

## Original 40-second media
- `render_film.py` — **exact source-controlled renderer** for silent H.264 educational film *The Word and the Ink*.
- `video-poster.svg` — original scalable static page poster (does not present false Play button).
- `captions.vtt` — six cues over exactly 40 seconds; B offers complete transcript without JavaScript.
- Actually rendered and visually inspected original six-scene offline film, not installed on site:
  - MP4: 40.000 seconds; 540×960; 12 fps; 480 frames; H.264; 104,965 bytes; SHA-256 `02a35c3374ad42e52486b3a53299c208b70b64c3eb6923c70fe021bff255e054`.
  - Exact Git blob renderer: `685980013e9b3b6820a545bd1b9b5f579507ba1f`, independently verified against the local executed source using `git hash-object`.
  - Offline review ZIP (MP4/poster/contact sheet/captions/HTML5 controls/renderer/README): SHA-256 `facdb2ee9fd50529221db97a98e96482be29745c0b38e9f5159de6aa7d6f8cbe`. ZIP integrity passed.
- No third-party embed, merchant creative, licensed stock footage, commercial message, or attribution pixel.
- Film is an *educational visual metaphor*, NOT a Stroop experiment or source of clinical data. Bars in scene 5 are explicitly labeled a diagram, not study data.

## Engineering proof and known limitations
- `tests.test.mjs` contains **18 independent Node tests**. Executed **18/18 test bodies PASS** against the exact GitHub-committed source contents with a V8 Node-compatible runtime and an adapted assertion harness. First run found a misleading test false-positive caused by the word "autoplay" in editorial prose; fixed to detect actual attributes and reran **18/18 PASS**. These are not a claim that native Node CI executed.
- Separately executed **8/8 native Python/ffprobe/ZIP media assertions PASS** against real local MP4, VTT and offline review package.
- A 29-item source-scoped QA pass initially produced **28/29** because the simplistic autoplay text regex matched prose; after remediation, exact committed test bodies passed 18/18. The initial failure is documented, not silently omitted.
- Confirmed real film rendered correctly, source Git blob matches local renderer, and 6-scene contact sheet visually reviewed.
- **Not executed:** full native `node --test` against exact committed repository snapshot, GitHub Actions on final SHA, WordPress sanitizer/block round-trip, real browsers at 360/390/768/1440/1920, keyboard/screen-reader WCAG 2.2 AA audit, Lighthouse/CWV, on-site caption sync, actual web A/B test, affiliate acceptance or revenue audit.

## Navigation and coordinated releases
- Organic/TikTok (suggestion-vs-Stroop educational hook, with paper attribution) → new independent investigation (only after publication) → optional existing /focus/ lead magnet → independent Zen12 buyer guide (only when published and validated) → official external merchant CTA ONLY after verified partner terms and earning URL.
- Preserve sole existing Jetpack Focus opt-in; no competing email list; the Dispatch Issue #174 owns newsletter drafts. The existing Jetpack excerpt-mode disclosure concern remains unresolved and no Zen12 draft is an approved email destination.
- Homepage flagship PR #49 and Issue #150, canonical Mind hub PR #172, QA Issue #126, and Dispatch Issue #174 are expressly outside this branch. No live WordPress CMS or navigation writes.
- Release blockers: written Final Vestige-specific Inspire3 acceptance; exact earning URL, cookie/tracking and allowed channels, written rights for any brand creative, privacy/affiliate purchaser data interpretation, release-time offer/checkout/terms/refund recheck, scientific/QD approval, first-party hosted MP4 with verified VTT synchronization, genuine keyboard/screen-reader/mobile/Lighthouse staging testing, founder publication authorization.
- Do not interpret clicks as merchant purchases or claim that A/B video improves conversion without field evidence.

## Verified source addresses (as of 2026-11-02)
Independent: https://pubmed.ncbi.nlm.nih.gov/12470132/ ; https://pubmed.ncbi.nlm.nih.gov/15994228/ ; https://pubmed.ncbi.nlm.nih.gov/16466414/ ; https://doi.org/10.1016/j.concog.2024.103730 ; https://pubmed.ncbi.nlm.nih.gov/38874567/ .
Official seller: https://inspire3.com/ ; https://zen12.com/hnp ; https://zen12.com/about ; https://zen12.com/research ; https://zen12.com/getstarted ; https://inspire3.com/privacy/ ; https://inspire3.com/terms/?s=zen12 .
FTC: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .
Site: https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; https://finalvestige.com/focus/ .
