# R76 controlled hypothesis — text-only source guide vs guide + original short film

**No experiment is active. No production tracking is authorized.** The film-versus-text comparison must not be represented as a demonstrated lift. This design remains isolated.

## User and outcome
The primary user enters through independently sourced perception research and seeks to decide whether a short structured audio program deserves their attention. Both variants deliver **identical buyer guidance** and the same inactive merchant control, and both provide complete reading paths without JS or video. Variant B additionally carries an OPTIONAL 40-second original illustrated film, with poster and synchronized-cue transcript concept. It adds no unsupported seller claims or extra offer copy.

The meaningful question is whether variant B increases *informed engagement* without harming trust, readability, accessibility, or performance—not just whether a play button is clicked. Before affiliate approval, ethically measurable research can focus on moderated qualitative comparison and synthetic testing only; no live visitors instrumented.

## Pre-register only after approval
- Allocation: genuinely randomized per visit via privacy-reviewed first-party mechanism, equal odds, same content inventory/offer controls, no user-level tracking; otherwise use consenting in-person usability comparison rather than silently randomizing public visitors.
- Primary metric (if active traffic use later authorized): **source engagement**, e.g. article citations opened/visited and continued reading, aggregated in approved privacy-safe analytics. Raw referrer URLs, full URLs with query strings, IP, cookies, device fingerprints, identifiers and purchaser records must never flow into this module.
- Secondary: optional guide open/read, film initiated when actually hosted, voluntary Focus route click and eventual reviewed outward purchase link click only after affiliate terms approval. An outbound click is **not a purchase**; partner sales must never be fabricated from events.
- Compare performance: LCP/CLS/INP or Lighthouse lab tests with web and video disabled/enabled; do not introduce performance regression or external trackers. A poster-only first paint is mandatory; no preload of video. Both variants keep no-JS text.
- A priori guardrails: near-CTA disclosure visually beside recommendation in both; no focus trap, low-contrast copy, tap target below 44px when relevant, forced sound, autoplay, inaccessible controls, or CTA bait. Film must be optional and silent; captions and complete transcript provided. The goal is not to imply an actual rubber-hand illusion happens in the user's browser.
- Exposure definition: page served with specific variant; not a cookie-identified individual; with tiny cohorts a random simple percent is not statistically reliable. No p-value or ROI claims with sparse data.
- Minimum privacy cell: synthetic aggregations suppress any bucket under 20. No partner purchaser names/emails/products accepted until legal/DP agreement and publisher privacy review. No collection now.
- Exit criteria: independent blinded editorial and claims review, hosted browser and WCAG QA, performance/SEO review, partner channel/link approval and explicit founder publication/measurement approval. If the optional video hurts page load or confuses the scientific conclusion, ship the text-only guide instead.

## Technical threat model and tests
- Link substitution: fail if marketer inserts an unapproved `href` to merchant checkout, cloaking redirect or unreviewed URL; keep native disabled button.
- Faux-disabled button: fail when only `class=disabled` exists but true HTML `disabled` attribute removed.
- Disclosure erasure: fail if removal or moving commission disclosure far from button.
- Split-brain content: fail if core guide diverges across A/B.
- Privacy leak: fail on extra event properties and deny any event stream in production; synthetic tests only.
- Covert signup: fail on new `form` or list vendor scripts.
- Cumulative scope creep: fail if branch touches existing homepage, canonical Mind hub, Dispatch, WP CMS/Jetpack, or deployment files.
- Media: verify exact 40.000 second H.264/540×960/12fps/480 frames, six VTT cues covering 0–40, native HTML5 controls and transcript; verify responsive 360/390/768/1440/1920 with actual browser. Local `file://` browser navigation can be blocked by sandbox; injected local HTML media checks are not staging proof.

## Organic SEO and internal-link intent
- Perception article: search intent “rubber hand illusion explained”, “rubber hand illusion suggestion experiment”, “Lush 2020 vs Slater Ehrsson 2022”; TikTok hook “Would you believe a fake hand was yours? The real mystery is the experiment's controls.” No guaranteed experience.
- Editorial route: article (when published) → Puységur → Focus Fieldbook; future curated /mind/ archive when canonical PR #172 is separately reviewed.
- Commercial route: source guide “Zen12 review evidence”, “Zen12 12 minutes research”, “Zen12 refund and privacy terms” → optional original film, free no-purchase test and **inactive** merchant offer block. No direct product CTA or list form in investigation.
- Maintain exactly one existing Jetpack Focus opt-in and welcome, no newsletter modifications. Dispatch #174 may incorporate source-aligned landing-page terminology only after independent editorial coordination and its own send approval.
