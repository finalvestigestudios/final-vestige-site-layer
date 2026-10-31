# Mind & Perception Studio R23 — Troxler evidence, Zen12 exact-offer warm-up, privacy QA

**31 October 2026 · ISOLATED DRAFT / RELEASE HOLD.** Owner: GitHub Issue #171. Nothing here authorizes publication, email, CMS, navigation, affiliate activation, deployment or modification of anyone else's branch. Homepage flagship PR #49 and homepage owner #150, Mind hub PR #172 and Dispatch #174 remain independent.

## Produced deliverables and preview route
- `investigation.md` (2,217 words): new original research-led historical/scientific article, **The Color That Disappeared Without Moving**, on Troxler's 1804 phenomenon, fixational eye movements, 2006/2008/2010/2013 experiments, source caveats and independent free non-diagnostic demonstration. No commercial CTA.
- `troxler-original-static.svg`: genuinely original accessible static vector demo with title/description, **no animation or image tracking**. `troxler-image-insertion-DRAFT.html`: WordPress insertion proposal only. The image URL placeholder is intentionally unhosted. Use source-managed media upload in approved staging, not live without release consent.
- `zen12-guide-A.wp.html`: complete evidence-reviewed WordPress Gutenberg Custom HTML text-only warm-up guide (approx. 1,500 content words; file token count includes HTML/CSS). Practical free 12-minute reflection, actual product-format explanation, evidence caveats, objections, alternatives, sources, disabled CTA with nearby prospective commission disclosure.
- `zen12-guide-B.wp.html`: **exact same substantive editorial/offer markup** plus optional original 40-second video storyboard component, inline original poster concept, full visible transcript. Video is NOT produced or hosted in this sprint. No fake player. Media will only activate after real first-party file, timed captions, accessibility, performance, separate partner rights/approval and founder publication approval.
- `zen12-40s-UNMASTERED.vtt`: first-draft caption beats, **not validated against any audio**. See `pilot-and-measurement-HOLD.md` for detailed story, creative rights, performance/a11y QA, predeclared A/B design and non-causal interpretation.
- `mind-hub-concept.wp.html`: distinct, styled, script-free four-stream /mind/ hub design comparison. Links only actual established live Puységur, Focus, Editorial Standards and Affiliate Disclosure pages. Does NOT overwrite #172 or alter WordPress.
- `claims-and-permissions.csv`: 52 individually source-linked rows across 17 unique URLs: merchant-advertised features, unsupported efficacy, independent science, FTC compliance, product rights and explicit commercial activation BLOCKERS.
- `measurement-OFF.json`: zero data collection, zero active partner URLs, no endpoint.
- `privacy-aggregate-OFF.cjs`: safe offline-only schema/aggregate prototype. Completely detached from either guide; rejects any extra keys (including identifiers), suppresses sparse cells and has adversarial synthetic tests. **Not a deployable event collector.**
- `qa.cjs`: exact-content source guards, colors/contrast math and mutation testing. Third-party, network, autoplay, form, tracking, CTA activation and shared-A/B-editorial drift tests.

## Research dates and provenance
Directly inspected **31 October 2026**:
- Exact seller catalog https://inspire3.com/
- Product offer https://zen12.com/about
- Exact order/review https://zen12.com/getstarted
- Seller scientific-copy page https://zen12.com/research
- Government endorsement policy https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- Government health-claims guidance https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- Scientific: https://pubmed.ncbi.nlm.nih.gov/16423702/ ; https://pubmed.ncbi.nlm.nih.gov/19146316/ ; https://pubmed.ncbi.nlm.nih.gov/20377283/ ; https://pubmed.ncbi.nlm.nih.gov/23940832/ ; https://pubmed.ncbi.nlm.nih.gov/17132081/ ; https://doi.org/10.1038/nrn1348
- Historical secondary bibliographic record https://www.illusionsindex.org/i/troxler-effect (Troxler 1804 original cited, **original German complete paper not independently read**).
- Meditation overview https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety
- Existing site (reported published in Issue #171) https://finalvestige.com/focus/ and https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/

**Merchant pages are seller statements.** Especially do not repeat as established a product-specific hour-of-meditation equivalence, automatic brainwave change, guaranteed anxiety reduction, wealth change, neurological reprogramming or medical result. Testimonials, timers, discounts and refund promises are not adopted.

## Test reproduction
From a normal Node.js working tree:
```bash
node mind/troxler-fading-r23/qa.cjs --mutation
node mind/troxler-fading-r23/privacy-aggregate-OFF.cjs --selftest
```
These are dependency-free static checks and offline synthetic measurement checks. They are not actual WordPress sanitization, browser/Lighthouse, hosted CI, screen-reader or video playback tests.

## Privacy model
OFF in both guide variants. The offline aggregate prototype and its spec offer only coarsened `period+variant+source+event` categories, reject non-whitelisted data, and suppress cells smaller than 20. It does not collect, transmit, save, or count real users, clicks or sales. Do not import the prototype into live pages. Pending independent user privacy requirements, consent, partner link terms, statistical design and release permission, **no outbound measurement can be activated**. There is no paid service or added email provider.

## Release and coordination gates
Independent editorial fact check (including German bibliographic attribution and scientific nuance), exact Zen12 offer check, written Final Vestige-specific merchant partner approval, SKU URL and website/social/email/creative/attribution terms, FTC review, formal refund/privacy scrutiny, original 40s film plus captions and tested player, WCAG 2.2 AA, no-JS, 360/390/768/1440/1920, 200%+ zoom, mobile keyboard/touch, first-party media failure, Core Web Vitals, source claims, source/CTA disclosure context, security/CSP and WordPress **staging** render. Site QA #126 independent review; #150 homepage art feedback ONLY; #174 Dispatch advisory ONLY. Founder must explicitly authorize publication separately from affiliate activation. Never merge or deploy merely because source tests pass.

## Proposed future navigation (not live)
Explore / existing archives → proposed `/mind/` → proposed `/mind/troxler-the-color-that-disappeared/` → optional existing `/focus/` / Puységur archive → proposed `/mind/tools/zen12-twelve-minutes-guide/` → *eventually* an approved disclosed, directly outbound earning link. No new seventh historical category or duplicate Jetpack form. Publishing or email sending is out of scope.
