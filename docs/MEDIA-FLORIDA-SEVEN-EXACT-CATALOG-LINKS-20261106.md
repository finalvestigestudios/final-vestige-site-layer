# Seven Florida Memory source paths and item-link integrity — 2026-11-06

This isolated, read-only audit covers published [post 432](https://finalvestige.com/2026/08/20/they-buried-the-dead-apart-okeechobee-1928/) (last CMS modification 2026-08-28T03:07:30). Sources: authenticated WordPress content (context=edit), the seven official Florida Memory item catalog index records, previous manifest blob `948bc1b65b42799aa40cfdb810ddf6ffd80886b6` and candidate blob `f737816bb8e7cf36b69834d8e3ed28d2839d8d`. It **does not repeat Site QA #154 browser collector** or modify homepage design.

## Source-level results (not browser proof)
All **7 exact stored image URL paths** match the official Florida Memory catalog's respective `Image URL` paths. They are on the `www.floridamemory.com` hostname. This is a URL-level provenance match, not a binary/crop verification. The official archive catalog is indexed; direct web-retriever opening of `www.floridamemory.com/items/show/...` returned a 403, and one direct image gave an unsupported redirected-resource error. **Neither establishes a logged-out visitor-browser failure**. The machine audit records all actual published image and surrounding link URLs; HTTP, decoded pixel geometry and cold transfer bytes remain `null`. All seven stored image tags omit explicit width/height; no actual CLS inference is warranted.

| Source slot | Official archive catalog | Candidate source/link/editorial action |
|---|---|---|
| 432:0 | [PR04493](https://floridamemory.com/items/show/4144) | 1928 Woodlawn Cemetery funeral. Keep distinct from the separate Black mass-burial service. Existing link correct. |
| 432:1 | [RC17068](https://floridamemory.com/items/show/38362) | **Avenue A, Belle Glade, Sept 1928**. Existing linked `hurricane3.php` generic exhibit → review exact item deep-link; broader ALT could be made more specific. |
| 432:2 | [RC10673](https://floridamemory.com/items/show/33289) | Destroyed auto garage Belle Glade, 1928; existing link correct. |
| 432:3 | [N031889](https://floridamemory.com/items/show/141398) | Pahokee State Board of Health headquarters, **1928**; catalog does not establish "post-hurricane disaster-response HQ." Candidate ALT: "State Board of Health staff at the Pahokee headquarters in 1928." No WordPress edit. |
| 432:4 | [RC04344](https://floridamemory.com/items/show/27848) | Coffins stacked by Belle Glade canal, 1928; generic exhibit hyperlink → item deep-link candidate. |
| 432:5 | [RC07668](https://floridamemory.com/items/show/30741) | West Palm Beach burial, 1928; search results hyperlink → item deep-link candidate. |
| 432:6 | [MSF-PB11548-001](https://floridamemory.com/items/show/340182) | **2001** photo of historical Black burial site, not contemporary 1928 imagery. Existing caption accurately says 2001; preserve. |

Three anchor changes would improve source integrity, **but image URLs themselves must not be rewritten solely on this evidence**. Archive source, original scene, date, credit and surrounding context are essential to historical accuracy.

## License, dimensions and performance gates
The [Florida Memory disclaimer](https://floridamemory.com/learn/about/disclaimer.php) and [Florida Department of State terms](https://dos.fl.gov/copyright/) require review; there may be other archive-specific reuse arrangements. Public catalog access does not automatically confer unrestricted mirroring. Keep per-item rights/credit `HOLD` until checked. Do not copy images or assume state material necessarily public domain.

After a *real* browser-broken image is documented by Site QA #154, verify exact picture/crop and any redistribution rights, record original binary SHA256 and native pixels (not physical print size), and only then generate a preview width `min(960,nativeWidth)` with aspect ratio unchanged/no enlargement. Stage (not publish) a licensed WordPress media candidate with srcset and catalog-credit trail; compare guest desktop/mobile `currentSrc`, HTTP and redirect chain, `naturalWidth`, image bytes, screenshots, and LCP/CLS. Distinguish 13 oversized original media-library files (43,522,829 stored bytes) from real page transfer; 76% savings remains **unmeasured**, historical 42 purported failures remain **unverified**.

**Production image fixes 0; WordPress writes 0; rehosts/downloads/caches 0; spend $0.**
