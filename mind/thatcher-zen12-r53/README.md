# Mind & Perception R53 — Thatcher illusion / Zen12 buyer-decision pilot
**Status: UNPUBLISHED, DRAFT, HARD HOLD — 2026-11-01**

## Scope and artifact manifest
This is an isolated additive review folder, not a WordPress plugin, release, homepage modification or replacement of the canonical Mind hub PR #172. Nothing in this branch authorizes CMS writes, active affiliate links, newsletter sends, a new email list, purchase tracking or website deployment.

- `investigation.md`: original ~1,757-word **The Face That Looked Ordinary Upside Down**. Historically and scientifically referenced Thatcher-illusion investigation. Zero commercial product naming, earning links or efficacy claims; illustrations are not experimental stimuli.
- `zen12-buyer-guide.md`: original ~1,669-word guide to **the precise public offer** at `https://zen12.com/hnp`, supporting seller About/Research/Premium checkout pages, free alternative, science boundaries, purchase objections, and no price/discount invented.
- `presell-a-text-only.html` and `presell-b-video-concept.html`: WordPress-friendly self-contained, scoped styling, **byte-identical ~11.5K-character substantive guide main HTML**. A is useful without a film, B adds original illustrated poster concept and a readable 40-second transcript in HTML `<details>`. Both preserve an adjacent clear prospective commission disclosure and a **genuinely disabled** merchant CTA. No active merchant links, active scripts, iframes, autoplay, email forms, pixels, analytics or event collectors.
- `film-storyboard.md`, `film.vtt`, `render_thatcher_film.py`: original six-scene 40-second *silent* schematic-film source. The reproducible renderer was executed offline with Pillow/ffmpeg and produces 540×960, 12-fps, 480-frame H.264 MP4. **The MP4/poster and functioning local HTML5 review player are offline reviewer artifacts, not WordPress-hosted media.** Poster and transcript are provided to illustrate Version B without a broken media player. Source renderer is committed.
- `mind-archive-noncanonical.html`: progressive, readable, accessible suggested Mind gateway respecting canonical hub PR #172, not a proposed live seventh category tile.
- `claims-permissions.csv`: **43 precise rows** distinguishing historical literature, science, seller-advertised product formats, unverified or prohibited outcomes, and absent partnership permissions.
- `sources-and-limitations.md`: source register and open verification caveats.
- `attribution.mjs`: **disabled** pure-function synthetic attribution proof. Categorical topic/channel/variant/action only; no personal fields, persistence, requests, or page hookup; aggregates n<20 suppressed.
- `verify.test.mjs`: native `node --test verify.test.mjs` suite for source quality, independent editorial separation, A/B parity, disabled CTA/disclosure, no external merchant anchors, B transcript, hub links, privacy and unsafe mutation defenses. An isolated V8 execution of fetched committed file content with Node-compatible assertions passed 9/9 groups; native Node/hosted CI execution has **not** been independently verified.

### Conversion design / evidence limits
**Hypothesis**: readers who receive a useful, scientifically constrained guide with one optional 40-second visual explanation may understand the offer, its risks and its boundaries better than readers of the identical text alone. This may not improve commerce conversion. The film is an educational introduction to Thatcher's illusion, not proof of Zen12 efficacy, not a testimonial and not an advertisement. Both versions provide the same guide, and the optional film can be bypassed; no forced playback.

A future authorized test would randomize stable **first-party** anonymous variant allocation without collecting IP, raw referrers, email, precise timestamps, UTM free text, or personally identifying data in the experimental output; compare consented aggregate guide reads and offsite CTA intentions, using predefined thresholds and clearly qualifying small-sample uncertainty. Do not enable a collection mechanism before privacy/legal review and explicit release permission. No conversion claims have been established. Never imply a click is a sale.

### Internal navigation / organic search / TikTok content map
1. A 30–45-second factual TikTok introducing original schematic face inversion -> full sourced Thatcher investigation **only when published**; original scientific evidence remains its own conclusion.
2. Full article -> optional existing [Puységur primary-source dossier](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/) as a methodological comparison, not as proof of hypnosis or meditation outcomes.
3. Separate /mind/ archive, only after PR #172 release, with four clear editorial streams: Perception & Attention; History of Suggestion; Practice & Reflection; Tools Under Review.
4. Optional free [Seven Day Focus Fieldbook](https://finalvestige.com/focus/) through **existing** Jetpack signup (no cloned subscription form, no changes to its 52-page edition, welcome automation or email provider).
5. Independent, directly reachable Zen12 source-checked buyer guide as a distinct Tools Under Review item; **no commercial CTA link until Final Vestige-specific Inspire3 acceptance/link and permitted promotional channels verified**.
6. Future outbound link would display unambiguous destination text with immediate commission disclosure; no cloaking, invented tracking parameters, affiliate redirects or hidden coupons. Dispatch Issue #174 owns newsletter manuscripts; this lane only owns presell proof/claims/measurement.

**Do not create new live navigation links to unpublished routes** or build homepage changes here. Consult Issue #150 and Site QA #126 for art/accessibility review only.

### Security, accessibility and performance QA matrix
- Text A and B: no JavaScript dependency, active merchant href, email input, automatic pixel, third-party embed, autoplay or broken video controls; button explicitly `disabled` and `aria-disabled=true`.
- Version B visual is **inline SVG** with `role=img`, `title`, `desc`; film transcript is true text content in native keyboard-operable `<details>`, not graphical captions.
- Native CSS scopes all selectors under `.fv53`; fluid 320–1920px layout, two-column hub collapses below 700px, native focus-visible, readable base font, constrained text column, and reduced-motion preference. This is source inspection—not proof of WCAG 2.2 AA.
- If video is later actually hosted, include HTML5 `<video controls playsinline preload=none>`, first-party poster and synchronized VTT captions. Do not embed pre-launch, autoplay, force audio, or rely on external services.
- **Unverified**: real WordPress staging render, WordPress sanitizer, visual QA at 360/390/768/1440/1920px and 200/400% zoom, screen readers and mobile touch, WCAG 2.2 AA, exact native Node execution, hosted CI, Lighthouse/CWV, actual VTT sync, real conversions, and partner-specific email permissions.

### Source, merchant, and release gates
Read `sources-and-limitations.md` and all 43 matrix rows. Standalone original research is not a clinical, financial, or commercial mechanism proof. The exact seller offer is a merchant description; product-specific extraordinary health or equivalence claims excluded. Buyer must independently inspect checkout/refund/privacy/renewal terms immediately before any purchase. Public creatives/swipe **do not** constitute affiliate approval.

Do not publish, merge, deploy, change WordPress CMS/media/navigation, swap Jetpack Focus welcome, enable attributions, add affiliate links, or send newsletter campaigns. Hard hold until (a) written Final Vestige-specific partner acceptance, (b) actual product earning link and permitted channels/creative use, (c) checkout/terms re-verification, (d) independent claims/FTC, privacy, accessibility, security and performance review, (e) founder authorizes the specific release. All non-commercial content retains independent editorial signoff.

### Reproduction
```
python render_thatcher_film.py             # requires Pillow and ffmpeg; offline only
node --test verify.test.mjs                # run in repo, test source is additive
```
No paid SaaS used or introduced. No vendor conversion performance has been asserted.
