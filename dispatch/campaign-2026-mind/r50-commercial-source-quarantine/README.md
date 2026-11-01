# Dispatch R50 — exact-source commercial citation quarantine (UNSENT)

**Stacked draft on PR #498; master Issue #174; companion Mind Issue #171.** Canonical PR #175, its six manuscripts, original 4-editorial/2-commercial allocation, and source-of-truth manifest remain untouched. This PR contains a mechanically derived **optional reviewer rendition of Issue 03**, not a founder-approved substitution. Never publish or send it.

## What was corrected, and what was not

The canonical Zen12 manuscript links directly to the vendor's purchase-capable website as source citations, although the issue says that its first-party buyer-guide recommendation is disabled. This creates a reader clickpath that bypasses the independent evaluation. The R44 auditor already demonstrated **two live vendor citations in three original source/preview formats**; those originals remain deliberately unchanged here to avoid hidden campaign substitution.

The new `issue03-proposed.md` differs from the canonical Issue 03 in **exactly two Markdown transformations**: `[sales page](https://zen12.com/)` becomes `sales page`, and `[About page](https://zen12.com/about)` becomes `About page`. Everything else, including its useful free 12-minute exercise, product specifications, NIH research, local guide placeholder, in-issue commission disclosure, legal-footer placeholders and HOLD warning, remains intact. Official merchant URLs are stored only in `source_registry.json` for editors, not in the proposed reader-facing email. R50 cannot and does not certify affiliate approval.

The corresponding `issue03-proposed.html` is a responsive, image-free, static HTML **internal review artifact**, with inline email-friendly typography, no forms, checkout, scripts, trackers, or active commercial anchors. It is **not** a Jetpack native preview or received email. `issue03-proposed.txt` is the corresponding review plaintext. WordPress's configured excerpt mode means an actual inbox message could still contain only a custom excerpt plus the site's Read More route; this preview must not be represented as the subscriber experience.

Two proposed **early-disclosure custom excerpts** for issues 03 and 05 appear in the source registry and are `NOT INSTALLED`. The founder-approved preheaders in the original manifest remain unchanged; a free-form custom preheader control in Jetpack is **not verified**. The custom excerpts are neither official preheader controls nor evidence of actual inbox rendering. WordPress documentation supports setting a post-specific custom excerpt and currently describes a **first 55 words** fallback absent an excerpt: https://wordpress.com/support/newsletter/settings/ (use https://wordpress.com/support/newsletter-settings/). Do not assume a separate 350-character rule or that any simulated excerpt has been delivered.

## Actual source alignment — checked November 1, 2026

* Zen12's official offer page `https://zen12.com/hnp` lists a 12-minute format, twelve-level full package, four styles and tier-dependent file counts, but its hour-in-twelve-minutes and automatic brainwave outcomes are **merchant representations, not product-specific independent proof**. See https://zen12.com/about for additional seller descriptions. Final checkout pricing, fulfillment and refund applicability unverified.
* Hypnosis Live's specific Total Focus seller page `https://hypnosislive.com/mental-skills/total-focus` currently advertises a 33-minute, 47-MB session and concentration claims. **Price display varies between page observations/search caches**, so omit exact prices and unconfirmed guarantee eligibility from outgoing copy. Product-specific email-marketing rights and tracked URLs unverified.
* FTC CAN-SPAM https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business requires accurate sender/subject, commercial identification as applicable, a valid sender postal address and a functioning opt-out; subscription status does not waive commercial-mail opt-out. Post publication is not email authorization. FTC endorsement requirements remain relevant to adjacent commissions: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking .
* WordPress native preview flow is described at https://wordpress.com/support/newsletter/email-appearance/ . The founder has **not** authorized a real test email or CMS write. Native editor preview is also unavailable via the current read-only connector pathway.

## Current authenticated production observation

At 2026-11-01 20:32 UTC, WordPress 256784396 reported subscriptions ON, can_send TRUE, new-post auto-email **OFF**, `email_content_format=excerpt`, featured images/date ON, reply-to no-reply, and `recent_sends=[]` (**no reported recent sends, not necessarily zero lifetime sends**). Welcome includes the existing 52-page Fieldbook; receipt unverified. Subscriber counts total=2/confirmed=2/unconfirmed=2 are inconsistent/nonadditive; the unique eligible count is UNKNOWN. /dispatch/ page #523, /focus/ #1579, Editorial Standards #17 remain published with no edits.

## Release remains closed

Every edition remains **HOLD_UNSENT**, and issues 03/05 additionally **HOLD_MERCHANT**. There is no accepted merchant email permission, no approved active earning link, no live approved commercial guide, no verified qualifying Final Vestige postal address or received-email unsubscribe, no private subscriber eligibility reconciliation, no received Jetpack MIME and no final founder approval of creative/audience/schedule. A preview or passing test does not lift any HOLD. No list contact, settings, WordPress edits, affiliate activation, tracking, spend or homepage PR #49 changes.

## Test

Run `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_r50_source_quarantine.py' -v` on the exact PR head, plus the complete stacked suite. Assert two-and-only-two substitutions, no active merchant links in any proposed rendition, source URL isolation, retained legal hard stops, and disclosures in first 55 words of proposed custom excerpts. Independently verify GitHub Actions exact source SHA and document pending genuine email evidence.
