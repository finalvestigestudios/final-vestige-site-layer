# R26 — Total Focus merchant, claim, and delivery due diligence (UNSENT)

Reviewed 2026-10-31, by Dispatch Studio. Source of truth: finalvestige.com/editorial-standards/ (WordPress page ID 17, read-only), Dispatch Issue #174, Mind Issue #171, draft PR #338 (parent) and seller-owned page below. Product-specific buyer guide ownership stays with Mind & Affiliate Studio; this audit grants **zero** affiliate permissions.

## Source matrix / supported use

| Source | What the source actually supports | What it cannot establish |
|---|---|---|
| https://hypnosislive.com/mental-skills/total-focus | Seller currently displays **Total Focus**, a **33 min**, **47 MB** recording with an audio preview, and markets large focus/productivity changes. | Independent effectiveness, a clinical result, checkout eligibility for FV, merchant email permission, stable pricing or refund fulfillment. |
| https://www.nccih.nih.gov/health/hypnosis | NIH NCCIH discusses research on hypnosis for selected health applications and limitations. | Does **not** test Total Focus, establish concentration-product efficacy, or endorse the seller. |
| https://books.apple.com/no/audiobook/total-focus-hypnosis-get-limitless-powers-of/id721837762 | Retailer metadata lists a related title from 2013 in a different distribution context, with different length and size. | It is **not evidence** the official seller's current 33 min/47 MB asset is identical to another store's edition. No claim of a product defect. |
| https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business | Sender accuracy, honest subjects, promotional identification where relevant, actual mailing address, functioning opt-out and obligation to honor requests. | A merchant-owned postal address, a rendered unsent HTML mock-up, or WordPress's `site_can_send=true` cannot satisfy Final Vestige release validation. |
| https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking | Disclosures of material affiliate relationships should be clear and conspicuous, placed where consumers will notice them. | An undisclosed commission link, generic site disclosure alone, or an unreviewed affiliate template is not adequate. |

## Copy audit — what changed from R25

The original email explained how to review hypnosis offers, but gave readers no **direct independent result** to obtain before encountering a prospective purchase. R26 opens with the measurement problem, adds a low-stakes, free three-minute observation, and explicitly states that it is not a clinical score or intervention study. That gives readers value even if there is never a valid affiliate agreement. The three buyer questions now distinguish *delivery format*, *outcome claim*, and *commercial downside*. The specific 33 min/47 MB numbers are clearly labelled as the seller's description. Two linked first-party/federal sources remain contextual, not proof of seller claims.

The external merchant page at 2026-10-31 showed price displays that differed materially from older indexed snippets. **Do not quote any current dollar price, percent-off, countdown, or refund window in an evergreen email.** A generic audio-session listing or retailer edition is not automatically the same as the seller's current SKU. This edition does not rely on claims about NLP, 'brain reprogramming', hypnosis changing income or productivity.

Safety: the copy explicitly instructs that guided hypnosis recordings not be played while driving or operating machinery. It does not suggest treating any health condition, replacing medical care, or guarantee an experience. The three-minute check does not attempt to diagnose ADHD or another medical condition.

## CTA/rights control

**Primary CTA** = an intentionally inactive `[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]` in issue #05. Reader-facing copy states the possible commission adjacent to the CTA; the live resource does not exist yet, and the CTA must not be replaced with a merchant URL. If and only if the Mind team has a published, independent, checked guide AND written partner approval for the email channel, inspect the approved landing page and earning link. Partner registration page or consumer promotional mail is *not* evidence of Final Vestige approval. No messages to merchant were sent in this sprint.

## WordPress deliverability and legal proof — all HOLD

Authenticated WordPress **read-only** snapshot at 2026-10-31 19:38 UTC: newsletter enabled, auto-new-post email **off**, `email_content_format=excerpt`, `recent_sends=[]`, confirmed counter 2, pending counter 2, WordPress total counter 2. The totals may be non-additive; eligible actual addresses have **not** been privately verified. Welcome email contains the 52-page Focus Fieldbook link as configured; actual confirmed receipt remains **not demonstrated**. We did not download, publish, import, send, or add accounts.

**Native Jetpack MIME delivery has not been observed.** Locally generated HTML/TXT and Gutenberg candidates do not establish WordPress full-text, preheader, opt-out, mailing-address, reply or legal rendering. Final Vestige must provide its own valid business postal address; never borrow WordPress/Automattic or Hypnosis Live's address. Explicit founder approval is required before a native email preview/test is attempted, and before any full/excerpt setting change. Nothing in this PR creates subscriber contact or consent.

The six-part pilot remains four editorial issues (01/02/04/06), two optional commercial reviews (03/05). All six `HOLD_UNSENT`, both merchant editions `HOLD_MERCHANT`. No A/B or performance numbers inferred from the tiny audience. Further affiliate, policy and checkout verification remains with Mind Issue #171. No homepage or production edits.

## Reproducible QA

`python -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_*.py'` and `node dispatch/campaign-2026-mind/tools/build_previews.cjs --check` verify reconstructed source and deterministic previews. These are **offline/local checks**, not CI, a native received email, or merchant consent.
