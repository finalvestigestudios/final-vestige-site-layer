# Attribution, accessibility, comparative test and release gate

**Draft specification only. Nothing below is installed on production.**

## Privacy-safe measurement

Future, consent-reviewed first-party **aggregate counters**, with strictly limited enumerations:

- mind_guide_view {page: "hypnosis-live-guide", variant: "text|video", source_bucket: "organic|social|dispatch|direct|other"}
- mind_focus_click {page: "hypnosis-live-guide", source_bucket}
- mind_offer_click {page: "hypnosis-live-guide", product: "total-focus", slot: "primary|secondary", source_bucket, variant}

Do **not** include or retain IP, email, account identifiers, raw referrer URLs, full query strings, device IDs, fingerprint signals, permanent cookies, user agents or cross-site IDs. Validate source_bucket against a fixed whitelist. Offer-click event code must fail closed when affiliate_url is null. Do not assert merchant sales from clicks; only verified partner sales reports can establish conversion. Do not cloak a merchant link with a local redirect or secretly add parameters the affiliate partner did not approve.

The present page uses **no JavaScript** and fires no events.

## Honest video vs text comparison

Version A = complete text-only guide and approved CTA. Version B = same guide plus an original 30–45-second optional video explaining the evidence and product-choice question. Video must not replace the text, must use a user-initiated play button (no autoplay or forced sound), poster, timed captions and accurate transcript, preferably first-party lightweight delivery after performance QA. If the video directly promotes a product, its sponsorship disclosure must be visible/audible within the endorsement, not merely down-page.

No video asset is available for this Hypnosis Live guide yet; the draft intentionally does **not** embed a broken media player. The existing Zen12 silent film preview is a separate product and not a suitable recycled Hypnosis Live endorsement.

Compare rate of qualified outbound merchant clicks from source-matched sessions and eventually partner-confirmed purchases. A two-subscriber mailing list is far too small for any meaningful A/B lift claim. Report raw counts and caveats until reach justifies a pre-registered experiment.

## CTA release transform

The draft contains two **inert span** states, not links, in sections carrying data-fv-offer-state="unverified". If and only if approved: manually replace each with a standard HTML anchor pointing to the permitted exact destination, with a clear descriptive label and appropriate rel="sponsored noopener noreferrer". Preserve a visible near-link disclosure in each same panel. Do not require JavaScript for the CTA to work. Check merchant deep-link policy before adding UTM tags or altering URLs.

## QA and approval checklist

1. WordPress Custom HTML staging preview 360/390/768/1440/1920 pixels; verify line breaks, contrast, portrait landscape, no clipped headlines, real touch targets, keyboard focus, screenreader landmarks and no nested main regions. Do not infer browser QA from source inspection.
2. Product source audit against https://hypnosislive.com/mental-skills/total-focus and FAQ https://hypnosislive.com/faq on **release day**, including actual checkout price, refund limitations and any upsell/prechecked controls. Today is October 30, 2026; specifics may change.
3. Source/claim review: current NIH, appropriate clinical literature, vendor distinction, no claims to have listened to the audio, no medical treatment or “100% sharp concentration” promises.
4. Affiliate approval, explicit product/program authorization, allowed social/email promotions, tracked landing URL and disclosures confirmed from authenticated partner account—not inferred from public recruitment page.
5. FTC clearly conspicuous material connection near each live link, and product-specific scientifically reliable substantiation for any health-related advertising assertion.
6. No second subscriber list, no changes to existing Jetpack/Focus welcome message; Dispatch Issue #174 owns all campaign emails. No homepage PR #49, Issue #150, Mind hub PR #172 or Zen12 PR #180 edits.
7. Independent site QA, founder editorial/design/release approval, verified canonical URL and link integrity, permission to publish. Until then this remains a draft source file.

No subscriber writes, analytics calls, email sending, merchant checkout, WordPress CMS writing, media upload or deploy is authorized by this spec.