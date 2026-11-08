# Apollo Experience 2.0 R218 — exact committed-source recovery (STAGING HOLD)

**Owner:** independent Apollo / Research Desk / Evidence Atlas lane (#150). **Business coordinator:** #820, charter #818. **Never edit** frozen homepage #49, homepage lead or Research Desk #158. This is a new isolated path, draft PR only.

## Real defect discovered and corrected in the test provenance

R217 PR #1604 at GitHub HEAD `5d40d61149838eb3c36d0c8a5a15ba22e31c71da` had a tested **local reference** builder that was **not** identical to its GitHub source. The reference Python builder's Git blob was `07f39a808768c58951b81ca849a8168a83929236`, while the **actual committed** builder Git blob is `769b574c14a37220d522e37ceaea01044630e3e7`. The reference QA script was likewise divergent and is NOT credited as exact-head QA.

R218 independently reconstructed the committed 8,559-byte R217 builder and verified its **Git blob SHA** byte-for-byte, then executed that actual source against pinned R216 staging inputs. The original reference produced R217 manifest SHA-256 `b29e28a0413e8c05294111c078c876ba8cfd5ab5bbab7d7e31b0d6505643c486`, while the exact committed builder produces `90fb65624990bd8b8f7c4184b0e74c2b51ad6004e7643ebc5b0740b5305c6e72`. **These are genuinely different output artifacts**, specifically PHP adapter, source-url crosswalk and WordPress shim. Do not use the earlier R217 reference ZIP as an exact-head distribution.

R216 input was validated against pinned parent manifest `a7546ae18c7970183c003ddcc4ac1bbc13f14cb87933982e6113a8792bec0128`. The R198 ancestral source chain is STILL NOT RECONCILED, so this is an exact R217 builder reproduction from independently pinned staging artifacts, **not** a canonical source-through-production reproduction.

## What this PR implements

`qa/rebuild_gate.py` independently refuses the wrong R217 Git blob, checks the pinned R216 input, runs the actual R217 builder, verifies the exact generated R217 manifest and every file hash, checks seven still-closed rights/creator/commercial/WP/release gates, and exercises the PHP normal/print/late fail-open/tampered-byte helper. It mutates the crosswalk, custody ledger and commercial gate to prove fallback. Using actual PHP-rendered markup and CSS, it runs Chromium responsive 320 / 360 / 390 / 600 / 768 / 1024 / 1440 / 1920, checks overflow, unique IDs, basic ARIA references, one free CTA, no active scripts/forms/frames, and keyboard disclosure. It writes deterministic screen hashes and a machine-readable HOLD receipt.

**Actual local work**: Exact-source independent build PASS; PHP syntax/normal/late/print/helper PASS; 3 tampered records fail open; Chromium 8/8 responsive fixtures PASS, keyboard and standard click PASS; no observed horizontal overflow. Screenshots generated and hashes retained. The explicitly separate javascript-disabled Chromium context timed out in this container and is **NOT TESTED**. Genuine axe-core, screen-reader AT, installed WP, external navigation, CI, p75 LCP/CLS, actual browser pinch/zoom and independent review also **NOT TESTED**.

The current original local test script used to verify this gate is not identical to the smaller source-controlled gate; retain **exact GitHub R218-head CI and independent rerun** as release blockers until that precise gate is run from the committed checkout. This R218 PR and its evidence are *staging research*, NOT a merge/deployment request.

## One relevant visitor pathway, not unrelated commerce

**Potential Grok Apollo 1 documentary (asset ID / platform post NOT VERIFIED) → Apollo Evidence Atlas with original NASA Review Board source and chronology → one contextual free investigation link → possible educator dossier (unsold hypothesis).** Mini Museum remains the independently selected primary affiliate offer elsewhere; inserting its products into the Apollo death-and-accident account would break reader intent and historical trust.

Source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . The Review Board described an arc as the most probable initiator, not a proven specific ignition point. NASA branding/media advertising restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . These source links establish editorial provenance, **not** promotional, merchandising, image, likeness or endorsement rights.

## Offer → funnel → blocker → experiment → evidence → owner

| Offer | Funnel step | Blocker | Experiment/change | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Possible educator dossier | Lead → paid purchase | No rights-cleared published SKU, merchant checkout or fulfillment | Validate real product, rights, merchant test, refund policy before commercial CTA | NOT VERIFIED / HOLD | Founder + Claude / commerce |
| Grok Apollo long-form | Social → Atlas | No authenticated published asset_id / post URL / hook | Praxxis read-only verify TASK-008; Grok owns media/posting | NOT VERIFIED | Grok + Praxxis |
| Source-led Atlas | Evidence → free original investigation | Previous R217 reference differed from actual committed builder | Reconstruct real source; verify PHP fallback, HTML route and responsive behavior | EXACT BUILDER PASS, STAGING FIXTURE PASS | Apollo |
| Authenticated paid orders | Qualified sessions → sale | No validated source cohort or merchant-confirmed order, refunds and fees | Separate outbound clicks/leads from actual orders; 7/30-day cohorts | NET REVENUE/1000 NOT COMPUTABLE | Claude/analytics + commerce |

**Release decision:** HARD STAGING HOLD. No merges, website, WordPress, creator, email, merchant, affiliate, analytics or spending actions. Only founder may approve production.
