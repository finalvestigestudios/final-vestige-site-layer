# R423 executed QA and release evidence — 16 November 2026

**Status: SOURCE-ONLY DRAFT / COMMERCIAL HARD HOLD.** Audit is limited to isolated `mind/r423/` additions. Does NOT authorize WordPress, partner links, email, social, deployment or merge.

## Actual checks (not assumed)

1. **GitHub content reread**: 9 exact branch files were fetched through the linked repository connector: self-hypnosis investigation, Zen12 A and B, SVG, VTT, four-stream hub, claim/permission matrix, conversion dossier, and Node verifier.
2. **Committed verifier actually executed in isolated V8 with Node fs/assert/path shims** over those fetched exact file contents: **23/23 PASS, 0 failures**. No native Node process or hosted CI run has been reported.
3. **Independent V8 static source inspection** found 48/50 checks on the *first* pass because the original unsafe-check regex wrongly matched innocent prose “no autoplay” and SVG's required xmlns. The committed verifier was corrected to distinguish HTML autoplay attributes from prose and embedded/external image URLs from XML namespace; the final committed verifier passes all 23 assertions.
4. **Adversarial mutation QA**: **12/12 unsafe mutations were detected** in an independent V8 check, including insertion of merchant anchors, enabling the paid CTA, deleting commission wording, script, form, iframe, autoplay attribute, javascript URL, inline event handler, broken VTT duration, and spoofed approval.
5. **VTT source timing**: six contiguous 7-second cues, 00:00:00.000 → 00:00:42.000. Timing source **only**, not synchronized to encoded audio.
6. **Buyer content parity**: the substantive buyer sections of variants A and B are byte-identical; B adds the optional scene storyboard and a lazy static original SVG poster. Both have fully readable no-JS content; one existing free Focus CTA; near-disabled-button prospective disclosure and no merchant URL.
7. **Claim matrix**: **31 classified claims, 20 source links, 28 commercial/release gates all HOLD/verified=false**. No specific FV publisher approval, exact channel/SKU permission, payout or assigned referrer checkout authenticated.
8. **Original article**: **2,908 whitespace-delimited words** with primary clinical trial, 2026 meta-review, 2023 systematic sleep review, 2020 myths/suggestibility sources, official SKU pages, FTC guidance, historical Puységur bridge and free nonmedical reflection.

## Important scope limits

- **NOT TESTED:** native Node runtime, GitHub Actions workflow, WordPress HTML sanitizer and saved CMS draft, real browser at 360/390/768/1440/1920, Lighthouse/CWV, screen reader, real keyboard and contrast, source/target redirects, playable 42-second video/audio, caption-sync, Jetpack subscription confirmation, permitted analytics, real merchant tracking, authorized checkout, completed payment, return, or settled commission.
- Existing 61-post baseline in Issue #171 is historical; later R422 authenticated connected WordPress figures were **66 published posts / 92 published pages**. The brief's original count is not presented as a current live audit. Live published Change Blindness, Mesmerism, Puységur and Focus URLs were checked in this run.
- 2025 self-administered hypnosis hot-flash RCT is **not** a Zen12 or attention trial. September 2026 clinical pain review finds modest improvement versus non-active controls and no clear superiority versus active interventions. Their scopes remain separate from seller claims.
- Seller main/order/alternate offer pricing and terms differ; no seller price, commission, earnings URL or medical guarantee enters the buyer HTML. Partner identity and right-to-promote are still unverified; Gmail consumer marketing is not partnership evidence.
- Commercial KPI **net realized revenue per 1,000 qualified human sessions = NOT COMPUTABLE**, with no settlement or audited cohort denominator, not zero.

## Source ledger checked this sprint

- Commercial: https://inspire3.com/ ; https://affiliates.inspire3.com/ ; https://zen12.com/about ; https://zen12.com/order ; https://zen12.com/secret/ ; https://hypnosislive.com/mental-skills/total-focus ; https://brainwaveshots.com/focus-shot .
- Independent: https://pubmed.ncbi.nlm.nih.gov/41217756/ ; https://doi.org/10.1002/ejp.70369 ; https://pubmed.ncbi.nlm.nih.gov/37399315/ ; https://doi.org/10.1002/acp.3730 ; https://pubmed.ncbi.nlm.nih.gov/31914365/ ; https://pubmed.ncbi.nlm.nih.gov/32744485/ .
- Historical/current FV: https://finalvestige.com/2026/11/02/mesmerism/ ; https://finalvestige.com/2026/11/02/change-blindness/ ; https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; https://finalvestige.com/focus/ .
- Regulators: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

## Ownership and release blockers

Founder/Commerce: named FV acceptance + exact Zen12 SKU, web/email/social channel rights, issued earning URL, approved referred checkout and refund/settlement terms. Claude: existing first-party consent/analytics, owned product checkout/fulfillment if a real SKU exists. Site QA #126: browser, mobile, WCAG/CWV, WP sanitizer, caption playback. Praxxis/Grok: authentic published media IDs and rights via TASK-008. Dispatch #174: exclusive newsletter/Jetpack ownership. Homepage art #150: information-only, no worktree changes. Founder: production publishing, spending, and partner activation approval. Source of truth Issue #171 + #820, charter #818.

**Next real release gate:** one authenticated sellable offer and independent paid settlement. More pages and clicks are not evidence of revenue.