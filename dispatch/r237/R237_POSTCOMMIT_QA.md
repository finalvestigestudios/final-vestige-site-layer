# R237 independent postcommit checks — 2026-11-09 09:32–10:xx PT

**Test input:** exact GitHub `dispatch/r237/` source bytes fetched at commit `e23ccf7d028e148432f946e7b4c56dad30f948ee`, with unchanged original campaign manifest from #175.

**Source scope:** SIX new files plus the ORIGINAL manifest; no changes to existing campaign originals. The reproducible Node runner `R237_SOURCE_TESTS.cjs` was executed in an **isolated V8** environment with mocked read-only `fs`, `path`, and `assert` dependencies, using exact committed JS and content blobs fetched with GitHub connector. It passed **1 clean baseline + 26/26 adversarial mutations = 27/27 assertions**. This is not native Node CLI execution, hosted CI, a WordPress email preview or a delivered-email test. The runner can also be executed with `node dispatch/r237/R237_SOURCE_TESTS.cjs` from a full repository checkout.

Tests intentionally rejected: subject/preheader drift (Markdown, HTML, plaintext), missing UNSENT labels, absent NASA official sources, replacement of approximate fifteen seconds with false precise timing, erasure of unknown ignition limitation, postal-address and unsubscribe placeholders, loss of one CTA, HTML scripts and tracking pixels, unsafe `javascript:` scheme, merchant tracking links, unsupported guarantees, missing merchant/delivery release holds, pretending Gmail no-match was proof of rejection, and changing the original 4 editorial/2 commercial count.

**Retrieved GitHub Git-blob SHA-1 identities:**
- `ISSUE04_APOLLO_ALTERNATIVE_UNSENT.md`: `fc54c20080aa27b5251ef409e17787674e6aa36d`
- `ISSUE04_REVIEW_ONLY.html`: `833f8a55aaee93439e391a706357b0fea0529fb5`
- `ISSUE04_REVIEW_ONLY.txt`: `7087ac515811e693a20c5a5b8e8033651cc0864c`
- `SOURCE_TRUTH_AND_CONVERSION_REVIEW.md`: `71d5b0384d53f8ec787faa3f959c457fd48d518f`
- `R237_GUARD.cjs`: `699de8f1a5f0baee17e4b5527d6163bac0a272f3`
- `R237_SOURCE_TESTS.cjs`: `7150fa425004b834d6cbdcf1990c1c48d685ff71`
- Original `manifest.json`: `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`

**Separate, earlier requirement:** the original six Python tests in #175 were previously executed natively 6/6 at R236 with eight byte-verified sources. R237 does not claim to have repeated that native run.

**Live verification:** WordPress newsletter status/settings retrieved 2026-11-09 ~17:32 UTC, `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=full`, `reply_to=no-reply`; totals 3, confirmed 3, unconfirmed 2, suppressed 0; actual eligible recipient count UNKNOWN, counts nonadditive; welcome PDF configured only, not receipt-verified. WordPress /dispatch/ page 523, /focus/ 1579, Editorial Standards 17 published/read. Public Focus and Standards pages read. Relevant NASA board and safety pages and exact merchant product/FAQ pages read. Official sources: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; https://sma.nasa.gov/sma-disciplines/accllp/apollo-1 ; https://zen12.com/hnp ; https://hypnosislive.com/mental-skills/total-focus ; https://hypnosislive.com/faq ; https://affiliates.inspire3.com/ ; https://jetpack.com/support/newsletter/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

**Restrictions:** all original six issues HOLD_UNSENT; 03/05 HOLD_MERCHANT; optional editorial 04 NOT ADOPTED; legal footer, native Jetpack preview, subscriber confirmation, partner email authorization, live merchant guides and independent paid purchases UNVERIFIED. No emails, test sends, WordPress posts/drafts/settings/list modifications, merchant links, analytics scripts, spending or website releases.
