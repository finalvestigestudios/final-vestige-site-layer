# R439 source and release QA receipt — 2026-11-16 PT

**Status: DRAFT / HARD HOLD / UNPUBLISHED.** This is a factual execution receipt, not a launch approval.

## Verified source checkpoint
Source content was fetched again from the GitHub branch through the connected GitHub file API after the two verifier corrections. Exact content-blob SHA receipts:

| File | Git blob SHA |
|---|---|
| `THE_LABEL_THAT_CHANGED_THE_TRANCE.md` | `797f1b6287e03195b3030d2a545cd73d37147b06` |
| `ZEN12_A_TEXT_ONLY.html` | `a67bf7c65ed0d090a808bd728f2aaf172e7b5529` |
| `ZEN12_B_FILM_CONCEPT.html` | `bcaa29a57b6d89fc068ea432dfdc92492a53ad29` |
| `MIND_ARCHIVE_WP_SOURCE_ONLY.html` | `46ae072af680ad46b81a21a9391d850e8c94e4ca` |
| `R439_ORIGINAL_POSTER.svg` | `abb0618f5308fef8c63c25659bba27cbfc93a841` |
| `R439_FILM_42S.vtt` | `b173e5e51f593f0e7f204e11a7d7d7dd297aae9e` |
| `CLAIM_SOURCE_PARTNER_AND_RELEASE_MATRIX.json` | `f7bd166d15e94a6d3e2c9ace4d651fd754d0c7b3` |
| `OFFER_CREATOR_ATTRIBUTION_AND_REVENUE_ACCEPTANCE.md` | `29323857f874200cdd7c82115951dd9600441157` |
| `verify.mjs` (corrected final) | `8b821c80669a01a6c84a41f0b38d6c136880f745` |

## Actually executed checks (no inflated CI claim)
- The **actual final committed verifier logic** was read from the above `verify.mjs` blob and executed in isolated V8 with a read-only in-memory adapter replacing only filesystem imports, `assert`, `console` and `process`; inputs were actual fetched GitHub file bytes. The shebang and Node imports were removed for the adapter only.
- **34 of 34 assertions PASS**: substantive A/B copy equivalence, semantic markup, merchant links disabled, contextual affiliate relationship disclosure near disabled CTA, absence of script/iframe/form/autoplay, no personal product-use claims, mobile/focus/reduced motion CSS, original accessible poster, six timed VTT cues, archive canonical sources, study citation, JSON claim-source graph, 28/28 release gates held, conversion event separation and creator-fit evidence.
- **12 of 12 deliberately unsafe synthetic source mutations detected**, independently reinvoking the same committed checks against read-only modified copies. Mutations included active seller link, enabling CTA, losing disclosure, adding third-party script, A/B copy drift, falsifying approval gate, inventing paid commission, losing citation, removing captions, inserting remote SVG resource, breaking free CTA and adding an email form. This validates the guard conditions against those examples, not overall software correctness.
- Initial audit found five literal/namespace test mismatches; the verifier was corrected before the final pass. The source copy was not weakened and the mandatory SVG namespace URI was excluded from a generic remote-resource check.
- Editorial manuscript **2,005 words** when split on whitespace; counted programmatically after fetching the GitHub blob.
- Official sources consulted: https://inspire3.com/ ; https://zen12.com/ ; https://zen12.com/about ; https://zen12.com/secret/ ; https://hypnosislive.com/mental-skills/total-focus ; https://brainwaveshots.com/focus-shot ; https://affiliates.inspire3.com/ ; https://doi.org/10.1111/psyp.70183 ; https://pubmed.ncbi.nlm.nih.gov/39032268/ ; https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance ; existing /focus/ and Puységur files.

## What is NOT tested
- Native `node mind/r439/verify.mjs` in a checked-out GitHub working tree: **NOT RUN**. The V8 adapter executed matching validation logic, but is not a native Node or hosted CI assertion.
- GitHub Actions / test statuses: **NOT CLAIMED**.
- Real Chrome/Safari/Firefox devices at 360, 390, 768, 1440, 1920 widths; keyboard/screen-reader WCAG 2.2 AA, Lighthouse LCP/CLS/INP: **NOT RUN**.
- WordPress Gutenberg sanitization, actual /mind/ draft content save, permalink/canonical, live link checks: **NOT RUN**. No CMS write is authorized.
- Real encoded and playable 42-second film, user-triggered playback and VTT timing/accessibility: **NOT RUN**. Only storyboard and poster/transcript/caption concept exist.
- Actual UTM delivery in platform in-app browsers, first-party analytics consent, Jetpack confirmed lead and delivery, legitimate merchant referred purchase and settlement: **NOT RUN**. No test checkout.
- Human copy and historical-source editorial review, actual seller-specific affiliate creative approval and legal review: **NOT COMPLETED**.

## Release governance and risk
All **28/28 commercial/production gates HOLD**. Named Final Vestige partner acceptance, exact SKU/channel permissions, issued earning URL, payable referral checkout/returns, owned-payable product, real Grok media IDs, independent verified paid commission, qualified-human denominator and net revenue per 1,000 are **UNVERIFIED / NOT COMPUTABLE**.

Only `mind/r439/` is intended to change on this branch. Final compare and PR metadata must be checked after the final receipt commit. No live WordPress, navigation, homepage PR #49, agent-owned Issue #150, canonical Mind PR #172, Dispatch #174, Jetpack welcome, Grok posting queue, new opt-ins, analytics deployment, affiliate links, paid acquisition, merge, or spending is changed. Founder approval and independent Site QA are required.

**Reproduction** once repository checkout is available: `node mind/r439/verify.mjs`. It uses only Node built-ins and reads local files, makes no external request, creates no files, and never authorizes a release.