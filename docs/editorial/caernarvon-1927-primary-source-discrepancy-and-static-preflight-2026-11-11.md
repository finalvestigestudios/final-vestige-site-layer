# Caernarvon 1927: primary-source discrepancy and structural release preflight
**Investigations Publishing Studio | 2026-11-11, 07:32–08:00 Pacific | DRAFT #2151 ONLY**

## Scope and release identity
- Authenticated WordPress post **2151**, *The Levee They Blew on Purpose*, status **draft**, modified **2026-11-11T06:40:26** (site-local).
- Latest source-controlled Gutenberg SHA-1 per existing authenticated audit: `6471d3770d66540f212fd240a7cf84933a50add1`. **Not independently re-hashed inside this note**; match the current post and issue #1589 again before any production-visual QA.
- Authenticated raw Gutenberg body reviewed in this cycle (81 top-level opening blocks). Neither this report nor the checks below changes the WordPress draft, site, theme, or homepage.

## 1. A demonstrable date conflict inside the historical research trail

The *1994 USGS Open-File Report 94-275* contains Donald W. Davis's conference chapter **“Crevasses on Lower Course of the Mississippi River”**, printed pp. 133 onward (passage at printed p. 140). The searchable USGS PDF says, regarding Bonnet Carré, **“Begun in 1932 and completed in 1937”** and refers immediately to operations beginning in 1937. This is **not** an accurate description of when the concrete spillway structure was built.

In contrast, the **U.S. Army Corps of Engineers New Orleans District** official *Historic Operation Information* page records that surveys began in **1928**, construction began in **1929**, and the main structure was completed in **1931**; guide levees followed in **1932** and highway/railroad crossings in **1936**. Its operating history begins with the **1937** opening. The **American Society of Civil Engineers** independently records **1929–1931** construction and **1931** completion.

**Source links:**
- USGS 1994 PDF, Davis chapter, printed p. 140: https://pubs.usgs.gov/of/1994/0275/report.pdf
- USGS collection/bibliography: https://www.usgs.gov/publications/processes-coastal-wetlands-loss-louisiana-results-a-multi-year-collaborative-study-us
- USACE New Orleans District *Historic Operation Information* (official HTML): https://www.mvn.usace.army.mil/About/Projects/Mississippi-River/Bonnet-Carre-Spillway-Overview/Historic-Operation-of-Bonnet-Carre/
- ASCE landmark history (independently retrievable HTML): https://www.asce.org/about-civil-engineering/history-and-heritage/historic-landmarks/bonnet-carre-spillway/

**Interpretation:** Davis appears to conflate construction/commissioning and the **first opening**, or to have introduced an erroneous completion date. Do not repeat Davis's 1932–1937 chronology as fact. The 1994 open-file collection explicitly identifies itself as preliminary and not formally reviewed for conformity with USGS editorial standards. This correction **does not automatically invalidate** Davis's historical Caernarvon diversion estimate; it raises the burden of checking his original dependencies and recognizing that institutional hosting is not a blanket accuracy guarantee. The current WordPress investigation does **not** state the erroneous Bonnet Carré construction dates, so no live or draft correction is required.

**Additional chronological safeguard:** The same 1994 chapter cites **A. C. Trowbridge (1922:13)** while describing the physical route followed by the **1927** artificial crevasse. A 1922 text can provide evidence about an *older channel's existence and geography*, **not eyewitness documentation of the 1927 detonation**. Its unpublished original has not been directly inspected. The existing WordPress investigation does not treat it as 1927 testimony.

**Discharge evidence (not measured counterfactual):** The Davis passage attributes roughly **9,202.9 m³/s** through the Caernarvon breach to a secondary chain including **F. Simpich (1927)** and **D. O. Elliott (1932)**. The 1927 original is identifiable bibliographically as Simpich, “The Great Mississippi Flood of 1927,” *National Geographic Magazine* **52(3):243–289**; **the article and underlying computations have not been inspected directly**. Exact-looking figures must be labelled retrospective/historically reported estimates, never a direct measurement of how much the demolition saved New Orleans. The WordPress text already does this.

### Source-access check boundaries
The historical paragraph of the USGS PDF could be retrieved as indexed/searchable document text through the research service. An attempt to inspect the actual PDF page image with the PDF screenshot service **returned HTTP 403**, so the text-based verification is NOT a page-image or normal-reader-browser PASS. The USACE official HTML likewise returned HTTP 403 to the crawler when opened directly; its search index supplied only snippets, not verified anonymous reader-access pixels. ASCE's HTML page did load for direct inspection. **Neither this source note nor a search-result snippet resolves the four-source ordinary-browser release requirement.**

## 2. Independent structural Gutenberg preflight — what passed, and what did not

Read the current authenticated post content (not an isolated substitute fixture) and checked the serialized block markup.

| Test | Actual result | Interpretation |
|---|---|---|
| WordPress identity/status | #2151 / draft / modified 06:40:26 local | Correct intended editorial item |
| Top-level Gutenberg opening blocks | 81 | Consistent with current release target |
| Major H2 section headings | 11 | Includes one anchored Sources & Further Reading section |
| Direct bibliography list items | 41 | Matches latest target |
| Documentary `<img>` elements | 4 | Correspond to previously rights-reviewed NOAA and LOC media |
| Missing `alt` on image tags | 0 | Serialized HTML has text descriptions; screen-reader quality must still be visually reviewed |
| Link occurrences / distinct href values | 144 / 54 | Structural counts only, **not** link accessibility checks |
| Internal `#fragment` links | 0 | No dangling intra-article references detected |
| Plain `http:` destinations | 0 | No obvious mixed-content outbound hrefs |
| Inline `<script>`, `onclick`, `onerror`, `javascript:` | None found | Limited static safety pattern scan |
| Evidence table | `figure.wp-block-table`, `tabindex=0`, `role=region`, `aria-label`, `min-width:720px` and parent `overflow-x:auto` | Appropriate scroll intent, **not** a rendered width/keyboard PASS |
| Featured media/social opt-out (authenticated post fields) | Featured photo #2148; `_jetpack_dont_email_post_to_subs=true`; `jetpack_publicize_feature_enabled=false`; `jetpack_post_was_ever_published=false` | First-publish suppression must still be sent explicitly |

**Limit:** This checks stored Gutenberg HTML/metadata, **not** the site's rendering, live frontend CSS/JS, network image loads, link destination integrity or source PDF accessibility. It must never be described as production preview PASS.

## 3. What still blocks first publish
1. An **authorized editor-authenticated** real WordPress production-theme *draft preview* at **390px and 1440px**, visually inspected and recorded against the exact latest WP revision, covering the header, four photos, original chronology, compensation graphic, evidence table, bibliography, reading map and mobile horizontal overflow. Never put private preview URLs/nonces/cookies in public GitHub.
2. A real **ordinary-reader browser content inspection** for the two linked USACE brochures and two linked USGS sources. A crawler 403, indexed PDF text or screenshot-service “ready” status without viewed image pixels is not dispositive. If a cited destination truly fails, use a proven accessible equivalent and explicitly qualify when only bibliographic details are corroborated; never quietly substitute a different report.
3. Only after both PASS: first publish **#2151** explicitly setting `_jetpack_dont_email_post_to_subs=true` and `jetpack_publicize_feature_enabled=false`, then independently read back the public URL, images, metadata, citations and mobile/desktop; tell Grok's separate social lane only after public QA.

**Release decision: HOLD / no WordPress publication this run.** No paid services, subscriber emails or social distribution authorized. Source note concerns the existing article; do not modify unrelated posts, the site theme or other teams' work.
