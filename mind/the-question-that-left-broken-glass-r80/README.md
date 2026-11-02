# R80 / Final Vestige Mind & Perception — misinformation × Total Focus

**Status:** UNPUBLISHED / HARD HOLD. This folder is isolated; no existing files were modified. It is NOT a production WordPress edit, a deployed website, a mailing list, a launched A/B experiment, or a live merchant referral system. Date: 2 November 2026.

## This sprint is substantively different

Earlier Mind pilots #172 and PRs #676/#687 cover the canonical hub and independently reviewed Zen12 video warm-up. They are **not overwritten or activated**. This pilot addresses a gap independently raised by the Dispatch Studio: newsletter #05 references the **specific** Hypnosis Live **Total Focus** product but no live/approved specific guide exists. It would be misleading to substitute a generic hypnosis-catalog article or a Zen12 guide.

The new investigation, *The Question That Left Broken Glass Behind* (about 2,419 words), reconstructs the misinformation effect with a 2025/2026 replication and methods bridge to the published Puységur archive. It contains **no seller links, promotions or product recommendations**.

The **independent named-offer guide** (about 1,773 whitespace-delimited source tokens) describes the seller's exact single **33-minute / 47 MB** Total Focus download and optional separate bundle, but no personal product use or effectiveness outcome is claimed. Offer pages and exact source register are in `claim-source-matrix.json`. Current sales page displayed different price from earlier search snapshot; both prices omitted. Seller advertises a refund but detailed terms were inaccessible, so mechanics are not represented as confirmed.

Two **complete** WordPress-compatible Custom HTML candidates are included: `total-focus-a-text.blocks.html` and `total-focus-b-film.blocks.html`, with **identical full substantive guide core** from `total-focus-guide-core.html`. B adds an original 40-second instructional story concept (poster treatment, six VTT cues, visible transcript) and marks the film as **NOT HOSTED**. No fake video player, source URL, autoplay or merchant link has been enabled. A standalone original film renderer/media may be added for offline review without adding media to WordPress.

A separate `mind-hub-noncanonical.blocks.html` previews the four streams, directly links only to published Explore/Puységur/Focus/standards/disclosure URLs, and leaves canonical Mind hub PR #172 alone.

## Exact audience / offer-fit

- **Audience:** readers who struggle to protect uninterrupted time and are considering a *guided 33-minute hypnosis-style recording*, not medical treatment or guaranteed cognitive enhancement.
- **Message:** use a no-cost three-day comparison first; learn what the recording actually is and which claims have not been established.
- **Seller-described features:** Total Focus; written/recorded by J. A. Amos; 33 minutes; 47 MB; single MP3; optional pairing with Whole Brain Thinking.
- **Seller-promised results that FV rejects as established:** 100% concentration, brain reprogramming via NLP, inbox clearance in minutes, enhanced career prospects and reliable on-demand productivity.
- **Objections:** different named SKUs, price discrepancy, quality/content unknown, session length, clinical limitations, return policy, privacy and potential sharing of buyer data.
- **Product link:** deliberately ABSENT until FV-specific acceptance, correct named-product and channel rights, exact link and legal/security review.
- **Disclosure:** near an actually disabled button: “If you purchase through a qualifying link in the future, Final Vestige may earn a commission at no additional cost to you.” A hypothetical future relationship is not stated as an existing one.

## Free editorial-to-reader path (proposed only)

TikTok/organic hook “The question after the crash” → original sourced misinformation investigation (no commerce) → optional existing free Focus Fieldbook `/focus/` (same existing Jetpack/Dispatch) → optional *separately distinguished* Total Focus independent buying guide → off-site recommendation only after merchant authorizes specific products/channels, founder approves publication, and all legal gates pass.

Do NOT link to currently unpublished articles from live navigation, upload anything, add new signup/list/pixel, edit `/dispatch/` or its welcome message, or present clicks as sales.

## A/B pre-registration (not running)

**A:** text-only guide; **B:** exactly the same guide plus original 40s optional visual educational story and transcript. The demonstration is about the misinformation effect, not the efficacy of Total Focus. Primary future outcome: consent-permitted, aggregated, qualified **off-site click intent per eligible guide view**, never inferred affiliate sales. Secondary: scroll-to-offer, optional video starts/completions (only if a lawful privacy-safe method receives separate approval), reader comprehension, accessibility and performance. Compare only after eligibility/permission and enough data; exclude all PII, cookies, raw referrers, user IDs and merchant customer records. No outcomes are asserted in this sprint. Small cells under 20 stay suppressed.

Hypothesis: an optional original film could improve comprehension/engagement versus the identical text guide, but could also distract, slow page load, or reduce click-through. Predefine stop criteria for accessibility, content confusion, performance degradation and privacy. Accessibility and source accuracy take precedence over conversion.

## Testing commands

```bash
node --test mind/the-question-that-left-broken-glass-r80/tests.mjs
```

Tests must run in a real Node runtime on exactly the committed SHA for a release candidate. Read-only source-scoped JavaScript-compatible adapter checks are an initial guard, **not a native Node or GitHub Actions pass**. A real browser, WordPress editor/staging, keyboard/screen-reader QA, first-party film hosting, captions, WCAG 2.2 AA and Lighthouse are separate unfulfilled gates.

## Frozen no-change and release boundaries

Do not merge/deploy/publish without release approval; no live WordPress CMS/menu/settings/newsletter/Jetpack edits. Preserve homepage PR #49, art/ownership Issue #150, canonical Mind hub PR #172 and independent Site QA Issue #126. Coordinate proposal with Dispatch Issue #174: email #05 is **HOLD_MERCHANT**; guide URL is not live. Public Inspire3 affiliate recruitment and unrelated Limitless Labs creative are not authorization. Default **no merchant buyer-level PII**.

Full source register, explicit 40 claim/permission decisions, and 14 false activation gates: `claim-source-matrix.json`. Synthetic-only tracking code: `attribution.mjs`. Film cues: `film-captions.vtt`.
