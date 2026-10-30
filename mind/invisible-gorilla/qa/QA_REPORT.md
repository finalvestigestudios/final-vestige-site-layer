# Mind / Invisible Gorilla — source-level QA report
**Date:** 2026-10-30. **Authoring branch:** feature/mind-invisible-gorilla-evidence-20261030. **Reviewed exact commit before adding this report:** 7ec3f35cbdcfb9e3aa8489723ff4ecd680dc1f83.

### Actually executed
A complete read-back from the GitHub API at the above exact SHA loaded article Markdown (16,835 characters), HTML (25,013 characters), 40-claim/12-source ledger (7,846 characters), navigation spec, bridge copy (9,611 characters), 42s-film script (2,680 characters) and committed tests/audit.cjs (5,243 characters). The committed audit function was **executed in the V8 Code Mode tool** against those retrieved bytes. Result **55 passed, zero failed**. This is NOT a claim that native Node in a GitHub-hosted runner completed, nor that WordPress rendered the page.

Creation-time preflight additionally caught an unintended active link to the seller in the HTML, and the builder was fixed before the successful source commit. Final source read-back verified no active merchant anchors, no JS/scripts, no user signup form, no video autoplay, no third-party images and no data collection. The source Markdown retains vendor-citation URLs for research traceability only.

An independent sRGB WCAG 2 relative-luminance calculation returned these **normal-size text AA numerical** ratios (not a rendered accessibility certification):
| Text/background pair | Ratio | >=4.5:1 |
| --- | ---: | :---: |
| Ivory body on dark background | 15.09:1 | YES |
| Muted text on dark background | 11.53:1 | YES |
| Mint links on dark background | 13.09:1 | YES |
| Gold heading on dark background | 10.93:1 | YES |
| Ledger card text on card background | 9.50:1 | YES |
| Unusual ledger label on card background | 5.92:1 | YES |
| Open-summary text on disclosure background | 11.25:1 | YES |
| Hero title on dark background | 16.55:1 | YES |

### Source and claim quality
- Original experimental evidence: Simons & Chabris 1999 https://doi.org/10.1068/p281059 ; Most et al. 2005 https://doi.org/10.1037/0033-295X.112.1.217 ; Simons 2010 https://doi.org/10.1068/i0386 ; Drew et al. 2013 https://doi.org/10.1177/0956797613479386 .
- Critical prohibited inference: “radiologists missed 83% of cancers.” The small 2013 sample searched for nodules and missed a **deliberately inserted gorilla**: 20/24 in this particular study. An eye fixation is not a clinical diagnosis or a transcript of consciousness.
- Commercial boundary: catalog https://inspire3.com/ and actual Zen12 offer https://zen12.com/about reviewed as *seller product positioning only*. The claim of one hour of meditation in twelve minutes is excluded. No research here trials Zen12's audio.
- FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance . The buyer-guide template proposes clear disclosure near any future earning link, **but none is active**. Affiliate account remains unverified.

### Not actually tested / blocking
- **Full WordPress staging**: page theme container, sticky header, WordPress block sanitize, site fonts, injected global CSS and live links.
- **Browser QA**: actual Chromium/Safari/Firefox viewport screenshots, device touch, 200% zoom, keyboard-only and screen-reader testing, axe-core, field Core Web Vitals/Lighthouse.
- **Independent editorial scientific review** and license clearance for any eventual third-party image/video; the current asset embeds none.
- **Merchant-specific affiliate account acceptance**: unverified; actual affiliate URL, payout, product purchase/refund terms, usage of seller promos and email authorization unknown.
- **Media:** 42-second film is a storyboard/script only, not produced or hosted.
- **CI:** hosted GitHub Actions has reported zero-step failures on unrelated repo workflows; no green test on the candidate. Independent QD and founder launch approval still absent.

### Release verdict
**DRAFT / HOLD.** No active affiliate links, no WordPress/CMS/navigation/Jetpack writes, no published `/mind/` path, no social posting, no Dispatch sends, no merge/deploy. This component is source-complete for staging review, not production-ready.
