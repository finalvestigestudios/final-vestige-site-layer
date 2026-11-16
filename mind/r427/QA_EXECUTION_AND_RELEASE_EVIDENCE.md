# Mind R427 — QA execution and release receipt (16 November 2026 PT)
**Scope:** additive `mind/r427/` source files exclusively. No homepage, canonical Mind PR #172, Dispatch #174, published CMS, live menu, Jetpack list, merchant checkout, affiliate tracking, social production, deployment, merge, email or spending changed.

## Source-control identity ledger (GitHub read-back)
All eight substantive files were read back from the isolated GitHub branch **after the final test fix**, and exact Git blob IDs recorded:
- `THE_VOICE_CHANGED_WHEN_THE_MOUTH_MOVED.md`: `6bca5e0495aec6221c13f9c94f9ad577c8c32832`
- `MIND_HUB_WORDPRESS_SOURCE_ONLY.html`: `9a4f95137de7b7fe2086746d972997c7327e3bf5`
- `ZEN12_A_TEXT_BUYER_GUIDE.html`: `86885b79d74d34709e2fda74d72458563c22bfef`
- `ZEN12_B_OPTIONAL_FILM_CONCEPT.html`: `bb3e39a7d92e007fd37b20a2590dfd79c6f6c821`
- `ZEN12_FILM_42S.vtt`: `3327c632d96514013871edf23eb9b3bd6578e7f1`
- `CLAIM_AND_PERMISSION_MATRIX.json`: `01778b4380d80af920c819b2869d44534f8ec31e`
- `CONVERSION_ACCEPTANCE_CREATOR_ROUTE.md`: `de70e6f49119186541139fa87a6c72332f890f4f`
- `verify.mjs` (corrected actual gate-open adversarial fixture): `33c6dd7c555f0a6430686703c2dd7c75de4ba51e`

## Executed tests — precise truth statement
Read-only execution of the **exact committed verifier source** in an isolated V8 JavaScript environment, replacing only Node imports/filesystem reads with GitHub-fetched exact file-content bindings and replacing console/process with recorders:
- **87/87 source-level assertions PASS, 0 failed, process exit code 0**.
- **10/10 deliberate unsafe mutations detected**, including 2 merchant-link injections, script/form/pixel additions, missing proximate disclosure, enabled purchase button, A/B copy divergence, forced-open gate in an actual tampered matrix fixture, and an offsite checkout tracking anchor.
- Verified: article source references and disclosed limits; 32 claim entries; 21 distinct claim sources; 28/28 commercial gates held; A/B text parity after removing B's one optional storyboard; no active merchant href, external pixel, script, form, iframe or autoplay; native-disabled purchase control, nearby conditional affiliate disclosure; mobile CSS breakpoints, reduced-motion and visible focus styles in source; four-stream hub links to existing public sources; VTT six continuous 7-second cues, exactly 0–42 seconds.
- One initial verifier fixture incorrectly made the held-gate mutation tautologically false. Replaced with an actual one-gate tampered matrix and reran all 87 checks PASS. This is a source-code check, not a merchant acceptance test.

**Not executed:** native Node in cloned repository (GitHub raw network unavailable in local container; container Node 22.16.0 installed, but source clone not obtainable), hosted CI/workflow, real browsers/360/390/768/1440/1920 screenshots, WCAG 2.2 AA contrast & keyboard testing, Lighthouse/CWV, WordPress block sanitizer, full encoded film and video playback, Jetpack signup/welcome delivery or consent, Grok media-ID/mobile links, referred checkout/transaction/refund, affiliate terms/approval, verified paid revenue.

## Source and seller documents reviewed
- 1976 Nature original study https://doi.org/10.1038/264746a0
- 2015 open-access variability https://pmc.ncbi.nlm.nih.gov/articles/PMC4580505/
- 2018 susceptibility https://doi.org/10.1371/journal.pone.0207160
- 2018 publication bias https://pmc.ncbi.nlm.nih.gov/articles/PMC6145544/
- 2025 Mandarin/English comparison https://pmc.ncbi.nlm.nih.gov/articles/PMC11987121/
- 2018 neural mechanisms https://doi.org/10.1152/jn.00262.2018
- FV existing https://finalvestige.com/2026/11/02/change-blindness/ ; https://finalvestige.com/2026/11/02/mesmerism/ ; https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; https://finalvestige.com/focus/
- Official merchant catalog https://inspire3.com/ ; program https://affiliates.inspire3.com/ ; Zen12 https://zen12.com/ and https://zen12.com/order ; Total Focus https://hypnosislive.com/mental-skills/total-focus and https://hypnosislive.com/faq ; Focus Shot https://brainwaveshots.com/focus-shot and https://brainwaveshots.com/faq
- FTC disclosures https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; health products https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance

## Non-negotiable blockers and acceptance
- No authenticated FV-named Inspire3 approval/issued earning URL or contractual channel, SKU, creative, price, return and settlement terms. Public commission advertising is not named authorization.
- No independently authenticated FV-owned paid Mind SKU. Existing 52-page Focus Fieldbook remains **free**.
- No genuine published Grok media ID and mobile UTM route matched to 3 candidates. Praxxis must check read-only via TASK-008; Grok retains content posting.
- Film B is a rights-cleared *illustrated concept and timed transcript/VTT*, not encoded or playable. Cannot claim A/B treatment tested, CTR improved or paid sales observed.
- Net realized revenue / 1,000 qualified-human sessions **NOT COMPUTABLE** due to absent verified settled purchases/refunds/fees and qualified denominator; an affiliate click or Jetpack form submission is not a paid sale.
- No release approval. **PR remains DRAFT; production and affiliate activation HARD HOLD**.

After GitHub PR creation, record its canonical URL and **exact final HEAD SHA** in Issues #171 and #820 and route scoped QA requests to #126/#150/#174. Do not update restricted owners' branches or work products.
