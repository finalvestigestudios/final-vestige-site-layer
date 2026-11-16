# R421 QA and source-control receipt — 2026-11-16 PT
**Release decision: HARD HOLD. Source-only draft / no WordPress write / no affiliate link / no merchant activation.**

## Exact-file audit execution (not a browser or native Node run)
From GitHub's R421 branch, fetched the entire committed UTF-8 blobs of the original 2,538-word research article, buyer guide A, buyer guide B, SVG poster, six-cue WebVTT, four-stream hub, 35-claim/28-gate matrix, conversion acceptance dossier and verifier. Each is under `mind/r421/`. A Node-API shim supplied file reads, assertions and basic path handling; the exact fetched committed verifier JavaScript (after removing only its Unix shebang) was **executed in an isolated V8 runtime**, not native Node. Result:

**R421 PASS: 29/29 assertions; 17/17 intentionally unsafe synthetic mutations rejected.**

The test exercises seller-anchor blocks, HTML script/iframe/form/remote image prohibition, genuine native disabled control independent of `aria-disabled`, near-CTA FTC commission disclosure, missing merchant permission, no-JS/no-autoplay policy, matching core buyer-copy, SVG alt/title/description/no embedded script, six contiguous 42-second WebVTT cues, four-stream hub, paper citations, 35 source-classified claims with resolved references and 28 false/held commercial gates. Reproduce in a Node >=18 environment (no install/network):

```bash
node mind/r421/verify-r421.cjs
```

The independent crosscheck initially reported 64 passed / 1 failure: a broad source guard mistakenly classified the film storyboard's plain-text phrase *no autoplay* as an autoplay control. Fixed to test active media/attribute markup, not prose. The committed verifier's first execution also exposed three real source-test gaps: an overly terse excluded-claim limit, assertions not matching the manuscript/dossier's actual boundary wording, and `aria-disabled` accidentally satisfying a permissive `disabled` regex. All were corrected on the same isolated branch and rerun. The final 29/29, 17/17 is **the passing post-fix result**, not a claim of browser, WordPress, or revenue QA.

## Files and claim categories
1. `THE_GORILLA_WAS_NOT_A_DEFECT.md`: 2,538-word original critical treatment of the 1999 experiment, 2010 familiarity follow-up, 2013 radiology extension and 2023 fast-motion qualification, with the 2024 medical review, a safe free exercise, and Puységur/Focus bridge.
2. `ZEN12_A_TEXT.html`: standalone source-only original longform decision guide with seller-precise tiers, styles, limitations, free option, five objections and inactive disclosure-forward CTA.
3. `ZEN12_B_OPTIONAL_STORYBOARD.html`: exact same substantive buyer copy plus an optional 42-second **STORYBOARD** with original poster and full timed transcript; not encoded playable video and no autoplay. Real A/B performance not measured.
4. `ZEN12_FILM_POSTER.svg`: original editable responsive graphic (source 1,593 bytes); not original researchers' footage and no permission to reuse protected footage assumed.
5. `ZEN12_FILM_CAPTIONS.vtt`: six contiguous cues, 00:00:00–00:00:42; caption script only.
6. `MIND_HUB_SOURCE_ONLY.html`: semantic four-stream 360px-first responsive HTML source; source-only, **not a saved WP CMS draft**.
7. `CLAIM_PERMISSION_MATRIX.json`: 35 claim rows / 21 exact source URLs / 28 commercial gates all HOLD; seller descriptions never automatically become independent evidence.
8. `CONVERSION_ACCEPTANCE_AND_GROK_CROSSWALK.md`: creator-to-article routes, one conditional high-intent Zen12 edition, fallback-owned-SKU proof criteria, separate click/lead/sale/commission events, 7/30-day net-revenue cohorts, owner/blocker matrix.
9. `verify-r421.cjs`: no-dependency reproducible offline source preflight and adversarial mutation tests.
10. This QA receipt.

## Independent source checks
- Primary: https://doi.org/10.1068/p281059 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC3563049/ ; https://pmc.ncbi.nlm.nih.gov/articles/PMC3964612/ ; https://doi.org/10.1073/pnas.2214930120 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC10973299/
- Exact seller: https://inspire3.com/ ; https://zen12.com/ ; https://zen12.com/about ; https://zen12.com/order ; https://zen12.com/secret/ ; https://hypnosislive.com/mental-skills/total-focus ; https://brainwaveshots.com/focus-shot ; https://affiliates.inspire3.com/ ; different product creative https://inspire3.com/ll/
- FTC: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- Live FV: https://finalvestige.com/2026/11/02/change-blindness/ ; https://finalvestige.com/2026/11/02/mesmerism/ ; https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; https://finalvestige.com/focus/
- Read-only authenticated WordPress post/page listings (Nov 16) showed 66 published posts and 92 published pages, rather than treating the older Issue #171 61/79 inventory as unchanged. The new counts require CMS interpretation; they do not authorize publishing.
- Connected Gmail targeted searches for publisher acceptance and owned Payhip product evidence found **no authenticated match**. A transient FORBIDDEN result occurred on one broad fallback search; this is insufficient to infer absolute nonexistence. The **approval state is UNVERIFIED**.

## Work that is NOT tested or represented as completed
Native Node runtime test, GitHub hosted workflow status, full browser layout at 360/390/768/1440/1920, screenreader and keyboard end-to-end, WordPress HTML/Custom HTML sanitization and CMS preview, live destination link resolution once rewritten for WordPress, actual encoded video/codec and caption sync, Lighthouse/CWV, Jetpack confirmation and attribution, real UTM/campaign IDs, actual authorized merchant checkout, independent transaction settlement/refunds/fees. The buyer guide source contains relative `.md` research links that must be **rewritten to final approved article route** before publishing; no live broken links were introduced because nothing was published.

## Ownership, evidence, metrics and protection
- Owner: Mind editorial & conditional offer only; homepage PR #49 and Issue #150, canonical Mind PR #172, Dispatch #174, live Jetpack/Focus, Grok social production queue and Claude analytics code remain untouched.
- Source-controlled preview is **BUILT**, static validation is **TESTED**, new site pages are **NOT LIVE**, eligible purchase and settled commission **NOT VERIFIED**.
- Founder/Commerce: genuine publisher approval OR actually payable rights-cleared owned SKU, permission/settlement & refund records.
- Mind/Site QA: encode film only after rights; accessibility, screenshot/breakpoint, browser and WordPress stage tests.
- Claude: no-duplicate existing first-party qualified-human attribution, consent and merchant reconciliation.
- Praxxis/Grok: 3 real social media IDs, factual hooks, platform-specific permitted URLs and rights, via existing TASK-008.
- Dispatch owns existing Jetpack newsletter editorial and welcome unchanged.
- Primary business KPI **net revenue per 1,000 qualified human sessions = NOT COMPUTABLE**, not 0, until a verifiable valid denominator and independently confirmed refund-adjusted purchase/commission exist.
