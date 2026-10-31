# R18 / Mind & Perception: The Letters Were There
**UNPUBLISHED, fail-closed editorial and Zen12 presell candidate** · 31 October 2026 · GitHub Issue #171.

This isolated sprint adds original research-led editorial and two **non-live** versions of an independently helpful Zen12 buyer warm-up. It does not touch or merge homepage PR #49, art Issue #150, /mind/ hub PR #172, Site QA #126 or Dispatch #174. No live WordPress CMS, navigation, Jetpack, email, affiliate purchases, tracking, paid SaaS or site settings are changed. Preserve the single existing Jetpack Focus signup/welcome.

## Files and scope
- `INVESTIGATION.html`: 10-section original ~2,300-word investigation of George Sperling's 1960 disappearing-letter/partial-report method, educational untimed/no-JS letter-grid illustration, source trail, historical Puységur comparison and free published Fieldbook. Source distinctions and merchant boundary.
- `ZEN12_BUYER_GUIDE.md`: ~1,800-word buyer guide for **the actual Zen12 offer and checkout**, four audio styles, seller-described 12 levels/12-minute recordings/48 MP3s, reasonable objections, current seller timer/privacy inspection, scientific limits, free 12-minute practice, and purchasing gate.
- `PILOT_A.html`: original fully written responsive Zen12 evidence/offer-guide candidate; no commercial checkout links, disabled CTA, visible commission disclosure, source links, free alternative, objections and 40-second visual transcript, no video.
- `PILOT_B_STAGING.html`: identical written content + **hidden unhosted** proposed first-party native video element. Review-only MP4/poster/VTT placeholder paths deliberately keep broken nonhosted controls out of sight. The separate PR #229 produced an actual 40s portrait film; this branch does NOT host or independently verify media, and the text concept must be compared visually with existing captions before activation.
- `EVIDENCE_MATRIX.json`: 60 individual scientific, seller, FTC, site and affiliate-release claims with 15 exact source URLs and explicit dispositions; all permissions and tracking fail closed.
- `EXPERIMENT_AND_RELEASE.md`: explicit video-vs-text hypothesis, accessible no-JS/focus/contrast/viewport plan, analytics/privacy-off design, internal links and release gates.
- `qa.cjs`: standalone Node source contract and harmful-regression checks with no third-party dependencies; see `TEST_EVIDENCE.md` for **actually executed** verification and exact GitHub readbacks.

### Reproduce source audit
```bash
node mind/sperling-zen12-r18/qa.cjs --mutation
```
Review the source and JSON claim dispositions. This test does **not** prove WordPress Gutenberg compatibility, browser/video accessibility, medical efficacy, publisher affiliate permissions or final site performance. Those require separate testing and signoffs.

## Primary/merchant guidance sources
- Sperling's original paper: https://sites.socsci.uci.edu/~whipl/staff/sperling/PDFs/Sperling_PsychMonogr_1960.pdf
- Sperling (1963) https://doi.org/10.1177/001872086300500103
- 2016 visual memory procedure https://pmc.ncbi.nlm.nih.gov/articles/PMC5019336/
- 2025 visual memory research https://link.springer.com/article/10.3758/s13414-025-03214-3
- Inspire3 official catalog https://inspire3.com/
- **Exact seller offer** https://zen12.com/about and **checkout** https://zen12.com/getstarted
- Seller free sample / other newsletter https://zen12.com/welcome
- Mindfulness 111 RCTs: https://pubmed.ncbi.nlm.nih.gov/37578065/
- Auditory entrainment inconsistencies: https://pubmed.ncbi.nlm.nih.gov/37205669/
- NCCIH https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety
- FTC endorsement/affiliate disclosure https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- FTC health claims https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- Puységur published https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/
- Focus published https://finalvestige.com/focus/

**Release status: HOLD.** Unverified exact account-specific affiliate acceptance, authorized SKU and earning link, creative, social/TikTok and email terms, product-specific efficacy, real WordPress staging QA, media first-party hosting/captions, full browser/AT testing, hosted CI, independent editor and founder publication authorization. This is an ethical conversion *hypothesis*, not a proven sales system. **Zero affiliate links activated.**
