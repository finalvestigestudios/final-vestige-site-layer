# R454 Test Matrix — Do Not Confuse Source Pass with Release Approval
17 Nov 2026 | HARD HOLD | Test owner: Mind + independent Site QA #126

## Automated static source acceptance (committed verifier)

The portable verify_r454.mjs script uses only native Node built-ins and checks:
1. Native HTML main landmarks, skip link and accessible card headings for both buyer variants.
2. Full substantive main text identical between A and B.
3. No active merchant/affiliate links, no embedded vendor scripts, no iframe, no forms, no forced video or autoplay.
4. FTC prospective commission disclosure visibly appears before a natively disabled buyer button, with current no-link statement; aria-disabled alone cannot satisfy this.
5. Free Fieldbook uses the existing live /focus/ route and does not create a second list.
6. Film's SVG poster has title/description, transcript and captions; only B has film; no actual video file asserted.
7. VTT contains six cues and terminates at 42 seconds; no overlap.
8. Hub is a source-only four-stream design with links to published, verified routes and no active merchant links.
9. Matrix parses, contains 36 labeled claims, 21 source URLs and exactly 28 uncleared release gates.
10. Docket manuscript identifies 1992, 1995, 2007 studies, counterexamples and explicit exclusion of Zen12 product trial.
11. Synthetic mutation rejection for activated merchant links, missing disclosure, removal of native disabled, invented prices, inserted external tracking, unlocked release gate and fabricated paid revenue.

**Node verifier is authored and must be run with:** node mind/r454/verify_r454.mjs (from repository root). A source-check run in a separate read-only V8 environment is reported only if actually executed and independently re-read from final GitHub blobs. Native Node execution, if unavailable, must be labeled NOT RUN.

## Independent staging and release tests still required (none implied by source QA)

- WCAG 2.2 AA real browsers: voice screen reader, multiple headings, skip link, keyboard and focus-visible, no-JS navigation, 360/390/768/1440/1920 breakpoints, zoom to 200%, color contrast, reduced motion, touch targets and disabled-button announcement.
- Genuine 42-second rights-cleared original playable file must be produced; validate native controls, autoplay OFF, caption track, visible full transcript, synchronization, correct video poster, keyboard use and pause function; set accessible loading behavior. As of R454, B is **STORYBOARD ONLY**.
- Compare page weight, critical rendering path, LCP, INP, CLS and requests on staging for both variants; film must not degrade mobile experience materially. Do not claim Lighthouse tests if none ran.
- WordPress block/HTML sanitation must be tested by Claude/Site QA on an approved isolated staging preview without live CMS changes; show screenshot or reproducible output.
- Claim QA must re-open seller pages on the release date and compare exact issued authorized SKU and checkout, dynamically changing amounts/discounts, tax, cart, upsells and actual refund terms. Separate promo /secret/ is not interchangeable with catalog.
- Evidence of named Inspire3 approved Final Vestige affiliate account, approved website/email/social channels individually, issued unmodified link, creative rights, and settlement terms must be recorded. Public signup page alone never counts.
- Jetpack confirmation and welcome delivery must be independently verified by existing provider logs under Claude/Dispatch without adding a test subscriber without approval.
- Grok/Praxxis must verify three ACTUAL published platform asset IDs with post dates, truthful hooks, licensed media, mobile-clickable permitted destinations and authentic link tags. Do not fill gaps with placeholders that look real.
- Claude analytics must show non-duplicative first-party tagged qualified-human sessions. Distinguish article-to-resource, confirmed provider lead, outbound CTA, merchant-confirmed order, refund/fee, and realized net revenue. Use 7/30-day cohorts and small-sample warnings.
- Founder and independent site QA approval required before any LIVE/CMS/affiliate/email/social deployment; a draft PR is not permission to merge.

## Rejection and rollback

If any real authorization changes, required creative is unavailable, the merchant changes checkout or the referred link fails, then automatically leave product CTA WITHHELD; do not redirect to generic merchant URLs as workaround. Preserve public Focus, Puységur and established navigation. If follow-on approved deployment fails security/accessibility/merchant/lead tests, roll back only its own isolated changes per Claude-approved release procedure. No removal of homepage PR #49, Mind PR #172, Agent Issue #150, Dispatch work, or Jetpack welcome.

## EVIDENCE ledger convention

Mark individually BUILT (committed), SOURCE TESTED (actual source inspection), BROWSER TESTED (actual browser proof), LIVE (explicit release confirmation), or MERCHANT VERIFIED (external independent settlement). The status of the entire launch is HARD HOLD until all relevant evidence exists. Do not infer commercial success from a draft page, a pass count, a newsletter subscriber or a social platform view.
