# R15 — Zen12 warm-up guide / optional 40-second film pilot / privacy and navigation
**Source-only preflight, 2026-10-31 · NO CMS PUBLICATION · NO PARTNER LINKS · NO EXPERIMENT RUNNING**

## The decision: write a useful buyer guide before a pitch

The text-only experience (A) is the complete [Zen12 evidence guide](./zen12-evidence-guide.md): original truth-first hook about a twelve-minute slot, seller's exact recorded course structure, independent evidence separating effects from proposed EEG mechanism, concrete five-minute no-cost practice, transparent questions and objections, research links, a separately demarcated unlinked offer area and a near-action financial disclosure.

The hybrid experience (B) uses **the same exact guide text and links, in the same order**. Between the hook and the first product-format section insert a compact, OPTIONAL original 40-second silent editorial film and its always-visible text/visual transcript. Do NOT let B truncate, reorder or conceal the caveats. Present media as extra context, never as proof that Zen12 works. No delay, scroll-jacking, modal, autoplay, looping, third-party player, background downloads or required click to see the article. Text must be fully available without JavaScript or media support.

This is **not** a claim that video converts better: it might increase comprehension or merely add distraction, bandwidth, and an extra point of failure. The product and ethical investigation should be strong enough if the reader never plays it.

## Assets are real but not published

Existing separate [Zen12 film draft PR #229](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/229) @ `dfffe093fcfcff6760cf6aeb981c788b2b10e23d` contains original Python source, SVG poster, `captions.vtt` (five 8-second cues), a timestamped visual transcript and a manifest. The original film exists as separately produced **review artifacts**, not media hosted on WordPress or a public CDN. Treat the previous measured hashes as documentary evidence only until the actual files are re-fetched and verified at upload.

- Portrait 540×960 H264, silent, 40.000s, 155,763 bytes, expected SHA256 `c4cb33fef60dfa773e65a46b9167c0581e58cf07f09c42b744f90c60af48ebbc`. Prior poster PNG 40,622 bytes, expected SHA256 `cce9065e7f4f53a34baefa628ad82af509a31f696b6e55f120d8645a6565b6e3`. Portrait large-type mobile treatment has never received full staging/AT approval.
- Widescreen 960×540 H264 silent 40.000s, 149,680 bytes, expected SHA256 `eb4a3f7e7d95ce5a6ff1ba08c83e66a4f7cc94cb1e3784bd51a330650c41ab00`; original 31,723-byte poster SHA256 `5b271178d83735c46df8c802d526ffcdeb01643b0b0b1672d32d335fb1059faa`. Earlier review flagged too-small text at mobile size, so this is **not** preferred on phones.
- Caption track and transcript need an actual timing/parity review against the portrait render. The film is silent and the captions duplicate meaningful on-screen statements; do not invent speech or product audio.
- Neither film is committed as an MP4 binary to this branch, remotely hosted, or publicly embedded; do not treat a source file name as an approved live URL.

## B treatment: semantic template (NOT ACTIVE HTML)

The implementation below is a **code specimen** for the WordPress stage *after* media rights, upload, URLs, hashes, captions, security review, tests, and founder release approval. It is deliberately in fenced Markdown, not live executable page markup. Replace placeholders only during a separately authorized release, never during this sprint:

```html
<figure class="fv-zen12-film">
  <video controls playsinline preload="none"
         poster="{{VERIFIED_FIRST_PARTY_POSTER_URL}}"
         aria-describedby="zen12-film-note">
    <source src="{{VERIFIED_FIRST_PARTY_VIDEO_URL}}" type="video/mp4">
    <track src="{{VERIFIED_FIRST_PARTY_CAPTIONS_VTT_URL}}"
           kind="captions" srclang="en" label="English captions" default>
    <p>This optional 40-second film may not play here. Read the transcript below.</p>
  </video>
  <figcaption id="zen12-film-note">Original, silent, 40-second evidence film. Optional.
  Product descriptions are the seller's; benefits have not been established for Zen12.</figcaption>
  <details open><summary>Full video transcript and visual description</summary>
    {{EXACT_VERIFIED_VISUAL_TRANSCRIPT_TEXT}}
  </details>
</figure>
```

**Preflight:** no `autoplay`, `loop`, `muted autoplay`, `data-src` JS hydration, Video.js, YouTube, Vimeo, external embeds, custom focus trap, hidden text reveal, affiliate CTA inside player, or analytics listener. Native controls must have visible focus and keyboard access. Poster contains no fake scan, MRI, testimonial or efficacy claim. Size media explicitly to avoid cumulative layout shift; prefer aspect ratio 9/16 on mobile, and avoid source-switching that downloads two videos. If CSS applies an aspect ratio, confirm it does not crop caption/overlay text. Provide transcript in normal reading order regardless of `details` support (for fully accessible final use, prefer a regular `section` with transcript always visible over collapsed `details`).

The film's closing commercial disclosure is not a substitute for the guide's adjacent, plain-language disclosure when and only when a real affiliate link is enabled.

## Disclosure component specification

```html
<section aria-labelledby="seller-review-heading" class="fv-product-context">
  <h2 id="seller-review-heading">Zen12: what the seller offers and what the evidence cannot confirm</h2>
  <p>Seller-described formats: twelve 12-minute levels, four listening styles and a 48-MP3 listed package.
  No independent product-specific support has been established for an hour-equivalence claim.</p>
  <p class="commission-disclosure"><strong>Commission disclosure:</strong>
  If you purchase through an eventual approved link, Final Vestige may earn a commission
  at no additional cost to you.</p>
  <span aria-disabled="true" class="disabled-offer">Partner purchase link not activated</span>
</section>
```

A noninteractive `span` is not a working button. It must not have click handlers, `href`, role="button" or tab stop. If and only if partner authorization is verified later, a reviewed `<a rel="sponsored noopener noreferrer" ...>` can replace the `span` beside the same disclosure. Check actual FTC compliance then. Seller's official publicly accessible `about`/`getstarted` URLs in the **sources section** are clearly labeled documentary sources, not affiliate purchase CTAs.

## Measurement: pre-registration, not hidden surveillance

**Current implementation: NONE. All collection OFF.** Do not add scripts, cookies, pixels, custom fields, localStorage, browser fingerprinting, exact timestamps, IP addresses, full external referrers, URL query strings, subscriber IDs, customer/order IDs, or postal/email/phone identifiers. Preserve existing Jetpack newsletter consent and welcome copy; do not create a parallel marketing list.

Before affiliate approval, a *manual* or opt-in usability review can evaluate two equally complete texts on comprehension, legibility, perceived transparency and perceived pressure. Ask: (1) Are twelve levels a format or an outcome? (2) Did you understand that an hour-equivalence claim was unverified? (3) Could you find the free option and source? (4) Did you notice any commission relationship? No respondent names or personal data are necessary. Label this qualitative editorial research rather than a conversion study.

After independent consent/privacy/legal review and authorization, pre-register a **single primary metric**: proportion of eligible guide views that click a verified earning link (conditional upon offer activation). An outbound click is not a sale, a sale is not profit, and a site's read event is not a conversion. A second metric may assess free Focus navigation. Predefine exposure time, analysis windows, exclusion logic and minimum effect of interest. If truly anonymous per-view assignment is not technically possible, do not install cookie-level tracking to force randomization; a convenience-sample user study may be more honest than an invalid A/B claim. If a privacy-safe randomizer is approved, use only aggregated daily counts by A/B and broad channel labels `organic`, `tiktok`, `direct`, `email`, `other`. Do not retain visitor-level join keys.

Measure and publish negative findings, video non-use, accessibility failures and load costs. Preflight media bytes (portrait MP4 ~156KB plus poster ~41KB), guide CSS/HTML budgets and real Lighthouse LCP/INP/CLS; ideally video bytes are fetched **only after a user activates play**. The text-only page must be meaningfully useful even if B loses.

## Navigation and acquisition: no draft URLs in live links

- TikTok 40-second organic educational story: “A face was ordinary upside down. Then the psychologist turned it right side up.” Include the 1980 citation visibly and tell viewers the effect varies; no medical/brain-training assertions. Seek engagement through the genuine mystery of the experiment, not a universal quiz score.
- SEO title: “The Thatcher Illusion: Why an Upside-Down Face Hides Distortion | Final Vestige”; description: “Read Peter Thompson's 1980 finding, the challenge from non-face studies, and the limits of what the illusion proves. Original schematic and primary sources.”
- Unpublished proposed route: `/mind/thatcher-illusion/`; do not add to menus, sitemap or Dispatch. The published historical archive remains at https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ and the *only* published free Focus funnel remains https://finalvestige.com/focus/.
- After independent release approval, conceptual `/mind/` PR #172 hub → Thatcher article → existing Focus; optionally editorial “Tools under review” Zen12 guide; crosslink 2010 non-face study and separately the existing unpublished change-blindness/Inattentional-Blindness drafts **only once each is published**. Do not promise live links now.
- Homepage team Issue #150: visual consistency review only (charcoal/ivory/bronze), NO PR #49 modification. Site QA #126: Gutenberg sanitizer, keyboard, screen readers, touch, 200–400% zoom, forced colors, reduced-motion, measured 360/390/768/1440/1920 viewport behavior, real browser caption/transcript parity, media rights, and negative case disclosure. Dispatch #174: informational source handoff only; no issue-draft edits or email sends. Use only published destinations in any future approved email.

## Permission and release checklist

1. Source accuracy independent editor checks exact original 1980 primary record, 1997 / 2010 / 2011 / 2014 caveats, 2019 / 2023 auditory reviews and seller page as of publication.
2. Confirm that all film source rights and caption/poster hashes are correct; hosted videos must actually load, be manual, meet a11y/large type and mobile performance thresholds.
3. Inspire3 account-specific acceptance and terms, exact Zen12 eligible product, tracking destination, creatives/brand rights, social promotion rights and **separately** opted-in email marketing permission; keep private agreements out of public repo.
4. Independent product/health claim compliance and FTC near-link disclosures; no seller auto-equivalence or guaranteed anxiety/focus/wealth outcomes.
5. Independent WordPress block sanitization and browser/AT/SEO/analytics security, Jetpack logged-out Focus form test without submitting real emails.
6. Founder visual, publication and separate merchant-link release approval. Keep this PR DRAFT until then. No publish/merge/deploy/CMS/nav writes now.
