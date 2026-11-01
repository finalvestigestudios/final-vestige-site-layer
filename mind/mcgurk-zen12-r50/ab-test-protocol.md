# Zen12 A/B pilot R50 — research design, instrumentation and ethical release contract
**Status:** Design only; both versions unpublished. No active outbound purchasing, no real audience assignment, no collection. Founder approval needed for each stage.

## Hypothesis and baseline
Research question: Does adding a genuinely useful optional original 40-second explainer to an otherwise identical independent Zen12 guide improve *informed* willingness to continue to the actual merchant offer, relative to text-only A?
- **A:** same 1,453-word guide core + purchase decision guardrails + eventual disclosed CTA.
- **B:** identical byte-for-byte guide core, with an additional original 40s silent conceptual film and fully readable transcript between guide and CTA. Never autoplay.
- The story is McGurk's *scientific method* distinction, not a product proof, audio entrainment demo or seller endorsement. B must not imply Zen12 created or approved the film.
- A visitor must be able to decide *not* to buy, consume the free twelve-minute exercise and visit the Focus Fieldbook without any signup. Commercial choice is deliberately optional.
- The film's estimated actual MP4 size is 121054 bytes (offline render); delivery optimization and host bandwidth unverified. Lazy media load only on deliberate play, first-party media, no external embed or player JS; do not place film binary in HTML payload.
- Revenue superiority is NOT the outcome measure; it is not scientifically or commercially established.

## What would count as evidence?
**Before affiliate acceptance:** run editor / QA usability checks only. No live commerce CTR, no artificial traffic or test sales. Evaluate whether representative readers can identify seller claims vs studies, read caption/transcript, locate free option, and understand disabled CTA. These are usability observations, *not conversion results*.

**After written approval, verified link, founder release:** use privacy-reviewed, explicitly consent-compatible server aggregation to compare actual *approved outbound link click intentions* divided by eligible guide visits. Clicks are not transactions. Do not claim sales or ROI without an authorized, properly aggregated merchant report.

Experiment validity: use a reproducible random assignment with no persistent identifiers **only after** QA approves its privacy and operational design. Do not compare organic Monday traffic to TikTok Friday traffic and call it an A/B test. Classify source only as direct/organic/tiktok/internal/unknown; never retain full referrer, URL query, IP, user agent, cookies, email, fingerprint, device ID or merchant ClickBank data. Randomization and de-duplication are unresolved release design questions—no pseudo-precision from raw repeat visits.

The pure module in this folder is deliberately limited: `ATTRIBUTION_ENABLED=false`, `recordLiveEvent` returns DISABLED, predefined categorical payload only for synthetic tests, no storage or network, only aggregate groups n≥20. It does **not** install analytics.

## Decision standard
1. Merchant acceptance + channel-specific permission for Zen12, exact product URL and creative rights; keep both versions HOLD before these.
2. Buyer-facing A/B layouts independently cleared by QA for accessible links, safe checkout redirection and no made-up merchant price/guarantees.
3. Captions timecodes match a first-party playable MP4; poster never misrepresented as play button; transcript fully readable with no JS.
4. 360/390/768/1440/1920 layouts and touch, focus, keyboard, 200% zoom and assistive technology checked on staging. Reduced motion supported.
5. Host behavior assessed with Lighthouse/CWV and real media delivery; reject B if it degrades usability or load.
6. Define primary metric and minimum detectable lift **before** assigning real readers; sample size/power determined from actual baseline, not invented. Confidence intervals and segment imbalances reported. A small/underpowered test is inconclusive, never a B victory.
7. Monitor *harm/quality* counters as veto: readers mistaking the film for product evidence, failing to notice disclosure, misunderstanding “seller-described,” or believing an outcome is guaranteed. A higher click rate cannot excuse deception.
8. Preserve existing Jetpack/Focus email funnel: one existing newsletter, no new signup form, no script pixel, no dashboard SaaS.
9. No seller testimonial reproduced, no permission inferred from public Limitless Labs swipe, no direct checkout citation in reader-visible content before authorization.

## Manual review procedure
- Open A; read through and compare headings/wording to B: **exact same source guide fragment**.
- Without JavaScript, verify all substantive reading, disclosures, free action, and muted disabled purchase control remain visible.
- Open B; inspect poster and transcript with keyboard. It does not pretend to be a functioning video player. Only after host review should a real native `<video controls preload="none" playsinline>` with VTT be introduced.
- Try to find a clickable merchant link, link shortener, tracking token, email capture, timer, unproven medical/financial promise, or fake play affordance: test FAIL if any exist.
- Independently check merchant page language against current exact offer; keep editorial factual independent. Compare claim/source matrix rather than a seller's marketing memory.
- Exercise native offline film with `offline-player.html` review package; note this is not WordPress staging and cannot validate production captions or CWV.
- Record exact branch/commit, browser versions, screenshots, source URLs and QA signoff in Issue #171 before proposing publication.

## Source & compliance anchors
FTC endorsement disclosure: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
FTC health-product claims: https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
2023 binaural beat systematic review (not Zen12): https://pubmed.ncbi.nlm.nih.gov/37205669/
Exact merchant sales: https://zen12.com/hnp
Seller About: https://zen12.com/about
Seller research: https://zen12.com/research
Public checkout reference ONLY for editor: https://zen12.com/getstarted
Generic affiliate program (not authorization): https://affiliates.inspire3.com/
