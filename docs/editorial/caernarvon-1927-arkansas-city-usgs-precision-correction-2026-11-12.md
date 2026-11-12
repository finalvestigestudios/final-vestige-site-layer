# Caernarvon 1927: Arkansas City peak-flow source precision, November 12, 2026

**Investigation:** *The Levee They Blew on Purpose*, WordPress DRAFT #2151. **Scope:** correction of **one existing Gutenberg paragraph block #28**, not a new article or publication authorization.

## Newly confirmed direct-source distinction

U.S. Geological Survey, *Selected Extraordinary Floods in the United States and Implications for Future Advancement of Flood Science* (2008), Appendix A, “Mississippi River near Arkansas City,” **printed pp. 231–232**:
- Original USGS PDF: https://pubs.usgs.gov/sir/2008/5164/pdf/sir20085164_AppendixA.pdf
- Separately indexed short appendix: https://pubs.usgs.gov/sir/2008/5164/pdf/sir20085164_MississippiRiver.pdf
- On p. 231, the **USGS Peak-Flow File published** a figure of **2,470,000 ft³/s**, footnoted as an estimate affected by regulation/diversion, for an approximate May 1927 flow **if the levees had confined the river**. The listed historical figures include **2,472,000 ft³/s** from *Handbook of Applied Hydrology* (Chow, 1964, section by Tate Dalrymple).
- On p. 232, reviewers describe the approximate **2,472,000 ft³/s** as an already-published USGS estimate, note that nobody recovered the original computation and recommend **rounding to about 2.47 million (or even 2.5 million) ft³/s**, retaining its status as an **estimate** rather than a measurement. The varying 2,470,000 and 2,472,000 conventions do **not** provide two independent peak observations.
- The **1,712,000 ft³/s** on April 20, 1927, at Chicot/Arkansas City, comes from historical reports of **current-meter measurements** before the peak, although the underlying field measurement sheets were not recovered by USGS reviewers. It is **neither the hypothetical May peak nor Caernarvon flow**.
- These amounts describe the *upriver* Arkansas City locality, not the flow through the intentional downstream Caernarvon opening and do not answer the historical no-breach counterfactual.

**Important source-access qualification:** Original USGS PDF text was obtained via the research crawler's indexed, source-attributed content, but the direct PDF page-image screenshot request returned **HTTP 403**, so this editorial check is **not** an anonymous ordinary-browser page-render PASS and does not close Site QA #1589.

## Controlled WordPress change and readback

**Previous revision:** modified 2026-11-11 20:42:03 Pacific, Gutenberg SHA-1 `b52d0225d81c99239c4e2336789999ceebfea858`.

**Correction:** edited only serialized core/paragraph section **index 28** with WordPress section-level optimistic locking against the previous post modified/hash and paragraph block hash. Added the source distinction between the **2,470,000 USGS Peak-Flow File entry** and the **2,472,000 published/USGS-repeated figure**, specifically named the rounding recommendation, and reiterated no measured peak. The April 20 current-meter caveat and linked 2008 USGS source remain. No alteration to conclusion, photographs, graphics, title, SEO, category, or bibliography.

**Independent authenticated WordPress readback:** site-local modified **2026-11-12 07:43:20 Pacific**, Gutenberg SHA-1 **`e89879d2b34a53de75d04f2a92bbab832de5aaf3`**. Exact current content has **81 top-level Gutenberg blocks**, **42 Sources & Further Reading entries**, four historical image blocks and two previously staged original evidence graphics. Status **DRAFT**, `_jetpack_dont_email_post_to_subs=true`, `jetpack_publicize_feature_enabled=false`, `jetpack_post_was_ever_published=false`; featured photo **#2148**. No subscriber email or automatic social posting.

**Visual provenance:** the existing four locally hosted documentary photographs (NOAA #2148, LOC #2255, LOC #2202 and LOC #2149) and original sourced explanatory figures are preserved, not swapped or newly generated. This cycle did **not** obtain an authenticated production-theme visual inspection, so metadata/structural existence **does not establish actual browser rendering**. The USGS numerical distinction is best communicated in text; creating a graphic that makes a reconstructed or hypothetical flow look measured would mislead readers.

## Release gate / QA handoff

[Site QA #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589) must now run the authenticated **390px and 1440px** production-theme preview + DOM/overflow/typography/image/table check against **`e89879d2b34a53de75d04f2a92bbab832de5aaf3`**, **not** prior `b52d...` or `62db...` hashes. In parallel check anonymous real-browser access to both USACE and both USGS document sources, or verify precise claim-equivalent replacements; automated 403 alone does not prove ordinary-reader failure.

Until those independent checks pass, **DO NOT PUBLISH**. No homepage, shared-template, other-post, social-platform, subscriber or paid-service changes. Editorial coordination: [Investigations #1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463). Grok distribution is a separate lane **after** successful live-page QA.
