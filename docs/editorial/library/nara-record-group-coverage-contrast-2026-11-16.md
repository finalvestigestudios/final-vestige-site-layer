# The National Average Hides the Archive — NARA coverage comparison

**FV Library Studio / 2026-11-16 / public release HOLD**  
Parent WordPress draft: [#2845](https://finalvestige.com/wp-admin/post.php?post=2845&action=edit). Coordination: [Issue #2777](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/2777).

## Reader problem
NARA's national **4.04%** textual-scan estimate describes the entire federal-record-group population. It can be misleading as a proxy for a particular agency's records. We compare ten individually attributed first-party record groups, using original artwork, an accessible offline HTML desk with local export, and a two-page printable receipt. We do not treat scan coverage as record survival, the chance of finding a named person, or a legal-access measure.

## Primary evidence — National Archives, checked November 16, 2026
Snapshot vintage **October 2026**: [Record Group Explorer](https://www.archives.gov/findingaid/record-group-explorer), **503,600,456** scans and **12,473,570,637** estimated textual pages, **4.04%** displayed. NARA's estimate is textual-record cubic feet × **2,500 pages per cubic foot**; records may contain other media and percentages can vary sharply by series.

| RG | Source | NARA displayed coverage | Online textual scans | Estimated textual pages |
|---|---|---:|---:|---:|
| 85 | [Immigration and Naturalization](https://www.archives.gov/findingaid/stat/discovery/85) | 93.28% | 48,103,135 | 51,568,700 |
| 29 | [Census](https://www.archives.gov/findingaid/stat/discovery/29) | 89.22% | 34,168,591 | 38,295,475 |
| 64 | [NARA](https://www.archives.gov/findingaid/stat/discovery/64) | 83.71% | 66,789,706 | 79,782,625 |
| 147 | [Selective Service](https://www.archives.gov/findingaid/stat/discovery/147) | 66.73% | 60,870,053 | 91,224,200 |
| 59 | [State Department](https://www.archives.gov/findingaid/stat/discovery/59) | 7.87% | 12,874,729 | 163,546,600 |
| 26 | [Coast Guard](https://www.archives.gov/findingaid/stat/discovery/26) | 4.87% | 8,005,382 | 164,490,700 |
| 75 | [Indian Affairs](https://www.archives.gov/findingaid/stat/discovery/75) | 4.26% | 8,040,408 | 188,624,550 |
| 21 | [District Courts](https://www.archives.gov/findingaid/stat/discovery/21) | 0.75% | 14,138,272 | 1,877,109,075 |
| 255 | [NASA](https://www.archives.gov/findingaid/stat/discovery/255) | 0.11% | 116,857 | 108,474,975 |
| 241 | [Patent and Trademark](https://www.archives.gov/findingaid/stat/discovery/241) | 0.02% | 142,759 | 656,912,175 |

**Interpretation:** these are NARA *online textual scans divided by estimated textual pages*, not counts of individual archival records or a claim that no patents/census materials are available from other services or repositories. See [NARA Catalog guide](https://www.archives.gov/research/catalog/help/using) for series-level descriptions and online-only search filters. Freeze the snapshot month and recheck before repeating numeric values.

## Assets, rights, and QA
Original FV 2026 explanatory bars, HTML software, worksheet, printable PDF. **No** NARA screenshots, archival scans, collection photos or third-party copyrighted media incorporated. Institutional resources are **linked**, not relicensed. Each source checked 2026-11-16; original and item-specific access and reuse conditions differ.

WordPress #2845 new **fourth** `core/html` section: *The National Average Hides the Archive*. Authenticated readback confirms four blocks, new section once, first three hashes unchanged, Library parent #77, status **draft**, noindex true. No existing public site changes.

Standalone Chromium `set_content` fixture checked 320/390/768/1440 × JS on/off **8/8 passed**, no horizontal overflow/page errors; comparison selects, receipt export, clear/reset tested. Direct `file://` navigation was **blocked by administrator**; fixture is **not** real-site browser proof. PDF 2/2 pages visually inspected, not PDF/UA tagged. ZIP integrity verified.

**HOLD** until real WordPress-theme viewport/keyboard/assistive-tech QA; anonymous HTML/PDF hosting and bytes, source-link/media checks; accessible PDF alternative; and explicit first-publication suppression for Jetpack email + social. The WordPress page connector does not expose `_jetpack_dont_email_post_to_subs` as writable meta. Do not publish solely because newsletter default is off. No emails, spending, Grok account writes or other pillars changed.

Potential Grok video premise only: “Four percent of the National Archives is scanned—until you look at the specific record group.”
