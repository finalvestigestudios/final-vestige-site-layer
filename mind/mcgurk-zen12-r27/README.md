# Mind & Affiliate Studio R27 — McGurk / Zen12 evidence-first conversion pilot

**31 October 2026 | DRAFT / UNPUBLISHED / HARD HOLD.** These files are isolated source-controlled candidates, not WordPress posts, live tracking or a released experiment. Owner: **Issue #171 only**. The original homepage PR #49, homepage/art Issue #150, Site QA Issue #126, Mind hub PR #172, Dispatch Issue #174, existing Focus/Jetpack signup and all live WordPress settings are expressly outside this PR.

## Actual research and current-state verification

- Read GitHub Issue #171 and most recent coordination comments, #150/#174 and existing #172/#346. Independently inventoried WordPress via read-only authenticated connector: **61 published post titles/excerpts**, **79 published page titles**. This does **not** mean every published article body was read.
- Read full live WordPress pages: Puységur's Animal Magnetism Files (page 1377), Seven Day Focus Fieldbook (page 1579), Editorial Standards (17), Affiliate Disclosure (14). Puységur's dossier is a documented historical research archive with 153 source rows and 16 case dossiers, including failed claims and coercion warnings. The Focus page is the existing 52-page free resource with Jetpack signup/Dispatch welcome; do not duplicate.
- Checked original McGurk/MacDonald 1976 source https://doi.org/10.1038/264746a0 ; John MacDonald's 2017 retrospective https://doi.org/10.1163/22134808-00002548 ; the 2021 task/response-dependent re-examination https://pubmed.ncbi.nlm.nih.gov/33884572/ ; Van Engen et al. 2022 https://pmc.ncbi.nlm.nih.gov/articles/PMC9894660/ ; Alsius et al. 2018 https://doi.org/10.1163/22134808-00002565 .
- Checked official **https://inspire3.com/** and exact **https://zen12.com/** home sales page, **https://zen12.com/about**, **https://zen12.com/getstarted**, **https://zen12.com/research** and public partner signup **https://affiliates.inspire3.com/**. These are seller-controlled, not independent product efficacy results, and no account-specific earning URL or approval is available.
- Checked FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking , FTC health product claims https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance and NIH overview https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety .
- Official Zen12 **three offer tiers** (seller descriptions, inspected 31 October): Beginner first 6 levels / 24 MP3s; Premium all 12 / 48 MP3s; Advanced final 6 / 24 MP3s. The getstarted checkout shows full 12/48 and its advertised extras; it is not evidence that each tier has identical checkout, price or rights.
- Seller markets 'hour in twelve minutes,' automatic brainwave shifts and health/attention improvement. Neither generic meditation studies nor a seller-run science page validate those specific outcomes. Do not adopt, even as a paraphrased promise or framed as already proven.

## Manifest (all additions under this directory)

- **investigation.md** (~1,983 source-checked words) and **investigation.wp.html**: original McGurk audiovisual perception feature; methodological counterexamples, source desk, free non-replication observation exercise, no affiliate links.
- **zen12-guide-a.wp.html**: complete original text-only purchasing guide with actual tier distinctions, a free twelve-minute practice, scientific limits, objections, near-CTA conditional disclosure and disabled offer button.
- **zen12-guide-b.wp.html**: exact same substantive guide plus optional original 40-second film **concept** with poster-style frame and readable transcript. A final hosted media master **does not exist here** and no fake play button is shown.
- **zen12-40s-poster.svg**, **zen12-40s-captions-draft.vtt**, **film-protocol.md**: first-party review-only design, captions draft and timed storyboard, NOT verified original synchronized media.
- **mind-hub-alternative.wp.html**: separate alternative /mind/ hub; no replacement for #172 and no new global navigation entry or subscriber form.
- **claim-evidence-permissions.csv**: **46 classified entries / 18 distinct source URLs**, including seller tier matching, proof boundaries, FTC, account permissions, media rights and privacy.
- **privacy-off.cjs**: data collection expressly **ENABLED=false**, only synthetic category inputs, strict unexpected-field refusal and suppression of aggregates <10; no server or live analytics.
- **qa.cjs**: source-level consistency and safety guardrails including negative mutation checks; requires Node.js for native execution.
- **navigation-experiment-gates.md**: exact internal-link proposal, SEO/discovery, editorial-to-commercial separation, measurement and release gate.

## No-Go design

No merchant CTA link, tracking query, affiliate cloaking redirect, cookie, third-party script, duplicate Jetpack/Dispatch registration, new email list, inflated source claim, medical/wealth outcome, fixed payout/price, personal testimony or reused seller creative. The site can be valuable without a sale. Don't place the disabled CTA within the scientific investigation: only the independent buying guide contains a clearly labelled *prospective* commission block.

## Reproducible local checks

From a checked-out repo with Node.js:

- Run: node mind/mcgurk-zen12-r27/qa.cjs
- Run: node mind/mcgurk-zen12-r27/privacy-off.cjs --selftest
- Independently inspect A/B source diff and ensure the only difference is the optional video concept section.
- Check the current official seller pages against **every tier**, not only the generic getstarted checkout, immediately before a future approval request.
- All source-level checks are a preliminary gate only. Neither a Node pass nor a simulated V8 pass implies hosted CI, full browser accessibility, WordPress block sanitization or sales performance.

## HARD release gates

1. **Partner:** account-specific written Inspire3 approval, approved individual SKU/tier earning URLs, confirmed tracking implementation and permitted web/TikTok/email channels; any approved creative/video rights and refund/check-out terms verified per exact destination. Public signup copy is not authorization. No product link until all confirmed.
2. **Editorial & claims:** independent assessment of scientific sources, original study/method descriptions, NIH boundaries, FTC near-link disclosures, accessible copy and any checkout obligations. Recheck latest merchant terms before approving.
3. **Media:** actual original 30–45s video encoded, measured and HTTPS-hosted; VTT synchronized to finalized spoken/on-screen content, WCAG track, controls, poster and always-readable transcript, no autoplay; no-JS access.
4. **Site QA #126:** actual WP staging sanitization of Gutenberg Custom HTML, mobile 360/390/768/1440/1920, keyboard/touch/zoom, reduced motion, NVDA/VoiceOver, contrast WCAG 2.2 AA, JS disabled, security/CSP, first-party media sizing and real Lighthouse/CWV. No untested claims of a pass.
5. **Homepage #150:** optional art-direction review only; do not touch frozen PR #49.
6. **Dispatch #174:** share tier/claim/copy correction with campaign owner; do not edit/send its six email issues; preserve established Jetpack welcome.
7. **Founder:** independent explicit authorization for publication, and separate authorization for affiliate activation, any tracking, homepage integration and any email send; do not treat a draft-PR approval as permission to release.

### Next iteration improvement

Prefer maturing one reviewed Zen12 guide into a single high-quality, source-supported destination over publishing scores of near-duplicate sales pages. Keep a single canonical guide URL once approved. The optional film is an experiment hypothesis, not a conversion claim.
