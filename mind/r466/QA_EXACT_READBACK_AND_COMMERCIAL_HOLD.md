# R466 exact-source QA and release receipt

**Checked 2026-11-18**. Unpublished, isolated source artifacts; no production WordPress, social, email, merchant or analytics writes.

## Actual execution

Eight files were read back through authenticated GitHub file retrieval on the R466 branch. Exact Git object blob identities:

| Source file | Git blob SHA |
| --- | --- |
| THE_SUGGESTION_BEFORE_THE_TRANCE.md | 4d947169facd415fa1fe46b88260c2600fa6ea9e |
| ZEN12_A_TEXT_GUIDE.html | 6fcd2e9128913f4190aaff48cafd00d521de3e06 |
| ZEN12_B_OPTIONAL_42S_GUIDE.html | 623cf14a65ed9e31608227e08bc7881305306b03 |
| ZEN12_42S_CONCEPT.vtt | 93c13d618006afa9c157a2efaecb92772c520842 |
| MIND_HUB_WORDPRESS_SOURCE_ONLY.html | 3c0fcf853b2368becf976a2b220dd12f479f519b |
| PRODUCT_CLAIM_PARTNER_RELEASE_MATRIX.json | f4e5ce5a28f198d93e473aef6dde5dca387ff7d6 |
| OFFER_TO_REVENUE_ACCEPTANCE.md | 3dadc822a527d6db551c3a072acba215a10f34c8 |
| qa.test.cjs | b63b3b5c235d0be809fa7602acedd534a349ea6b |

Independent read-only JavaScript/V8 assertions were actually run against the eight committed blob *contents* and yielded **36/36 PASS**. Explicitly checked source article citations and length (>2,000 words), historical provenance, textual substantive parity of A/B, disabled controls, adjacent prospective affiliate commission disclosure, no executable scripts/signup form/earning URL, no active video or autoplay, accessible SVG, optional transcript, six VTT cues ending at exactly 42 seconds, mobile CSS, reduced-motion, all four hub streams, currently live articles, merchant-specific source decisions, 38 matrix claims, 24 source URLs, 34 release gates still HOLD and revenue NOT COMPUTABLE.

Three of these checks were deliberately corrupted in memory and the safety checks detected all **3/3**: removing native disabled status, inserting an external script and falsifying a commercial gate to PASS. These are narrow smoke tests, not fuzzing/security certification.

## Reproducibility

The branch includes a standalone zero-dependency **Node native test suite**: node mind/r466/qa.test.cjs from a real repository checkout. The file was authored and blob-verified, **but it was NOT executed with Node** in this sprint; do not report its asserted test count as executed. Separate static V8 assertions above were executed. PR/CI status requires independent verification.

No authentic full-browser, Playwright, Lighthouse, WCAG 2.2 AA assessment or WordPress sanitizer test took place. No external merchant, Jetpack confirmation/delivery, tracking, checkout, settled commission or actual human A/B test ran. The original B poster/transcript/captions are **not encoded playable video**. No public /mind/ route or WordPress draft was created, and the source-only hub is not published.

## Claim and creative release hard holds

- Inspire3 named Final Vestige-specific partner acceptance, exact allowed SKU, web/social/email channel permissions and issued earning link — **HOLD**.
- Exact eventual authorized checkout price, applicable refund/delivery/support contract, settlement and refund reversals — **HOLD**. The public standard and secret Zen12 pages are different contexts.
- Clinical efficacy: seller claims excluded; primary studies summarized from PubMed records, full-text risk-of-bias/clinical review **NOT COMPLETED**.
- Actual 42s film, poster rights, captions, keyboard/no-JS/motion/sound, media MIME/CSP, mobile/browser and performance — **HOLD**.
- Actual matched Grok video IDs/rights/hooks/mobile destination — **HOLD**.
- Existing Jetpack confirmed lead/welcome delivery and merchant-confirmed sales — **NOT VERIFIED**.
- Paid owned FV Mind SKU, licensing/fulfillment/returns — **NOT AUTHENTICATED**.
- Paid conversion and refund-adjusted net per 1k human sessions — **NOT COMPUTABLE**.
- Founder production/revenue approvals, Site QA, homepage art owner and Dispatch coordination — **HOLD**.

Artifacts were created **only under mind/r466/** in a new isolated branch. This is not authorization to merge, publish, link a merchant, send email, track visitors, or modify PR #49, Mind hub PR #172 or homepage Issue #150.

Official external sources: https://inspire3.com/ ; https://zen12.com/about ; https://zen12.com/secret/ ; https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .
