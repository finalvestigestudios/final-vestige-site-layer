# Flagship release qualification — actual staging measurements and image-rights custody
**2026-11-02 | DRAFT/HOLD | proposed production is NOT authorized.**

## Exact release baseline
- Parent: draft PR #613, exact HEAD \`ca5ff6ac32cda9c774ccd33e1ab292ac450c0ee2\`.
- True private WordPress/Assembler + Chromium five-width passing CI: GitHub Actions run 41434543141; artifact 13135916960, ZIP SHA-256 \`7cd66ca0a4b37823b41b998c833b9061de2a5b7821420c84c416820d9b4b17c8\`.
- \`STAGING_ACCEPTANCE.json\` directly reports unthrottled Playwright LCP entry start times 360px **824 ms**, 390px **848 ms**, 768px **912 ms**, 1440px **988 ms**, and 1920px **NULL / NOT MEASURED**. It reports CLS **0** at all five widths. These are **one-off local/browser observer values**, not 4G/mobile Lighthouse scores, real-user p75, or WordPress.com hosted data. Absence of an LCP entry at 1920 MUST NOT be converted to a pass.
- The same receipt shows all 15 actual selected-image HTTP 200 / decoded media payload checks and zero axe WCAG-tagged findings at five widths. Neither establishes rights clearance or complete WCAG 2.2 AA.
- New companion \`measure_private_lab.py\` runs measured, cache-disabled authenticated renderer trials with CDP 4x CPU + 150ms RTT / 1.6 Mbps at 390px (twice) and 1440px unthrottled (once). Results are independently recorded to sanitized \`THROTTLED_CHROMIUM_LAB.json\`. The lab fails closed on missing/invalid LCP/CLS, wrong viewport or chapter count, or LCP >2500ms / CLS >0.1. Its throttling model is **NOT Google Lighthouse** and its LCP/CLS are **NOT field CWV**. Do not call these thresholds a production pass until measured actual results exist.
- Lighthouse mobile/desktop scores, INP field data, Safari/WebKit manual test, 200% zoom and screen-reader walkthrough, WordPress.com Personal sanitizer/cookie/Jetpack compatibility remain **NOT TESTED**.

## Archival-source rights / story-integrity review
| Exhibit and exact source | Supported evidence | Rights/claim boundary | Gate |
|---|---|---|---|
| Apollo 1 crew photo, original media WP ID 473, candidate \`s67-19766.webp\` | NASA's Apollo image and Apollo 204 Review Board source links are embedded in the homepage evidence card. NASA Brand Center / Media Usage Guidelines generally permit factual editorial reproduction, while NASA emblems/identifiers are specially controlled. | The image cannot imply NASA endorsement of Final Vestige, the Focus Fieldbook, Inspire3, or any commercial product. Keep NASA credit and non-endorsement beside accessible source record; do not use as an advertisement hero. | **EDITORIAL USE CONDITIONAL** on attribution, image identification and no-endorsement QA. |
| Franklin Victory Point note, WP ID 474, \`Franklinexpeditionnote.jpg\` | Wikimedia Commons file page names the 1847 original note and April 1848 addition; displays public-domain marking. Existing candidate accurately distinguishes typographic hero from facsimile and links original scan. | The digital reproduction's precise provenance and U.S. public-domain rationale must be confirmed from file history/licensing; Commons file page includes caution about a U.S. public-domain tag. Don't imply the museum produced the Commons scan. | **PUBLIC-DOMAIN MARKING DOCUMENTED; ITEM-LEVEL SOURCE REVIEW REMAINS**. |
| Malbone/BRT 1903 Brooklyn map, WP ID 1258, NYPL image ID 5003296, item UUID \`c745e730-d2a9-012f-5ecc-58d385a7bbd0\` | NYPL Research Guides identify this exact \`[1903]\` system map, its creator Street Railway Journal and role in early BRT history. Candidate links NYPL catalogue and states that it predates the 1918 wreck. | NYPL's general policy and API enumerate No Known U.S. Copyright/CC0/Managed/Undetermined at the **capture/item** level; a general policy is NOT a rights statement for this particular scan. The current candidate says NYPL believes *this item* is public domain, but an independently retrieved, item-specific right statement is still absent. Public catalogue direct fetch returns HTTP 403 in this review environment. Keep map as historical context, never a 1918 Malbone curve-site survey or exact overlay. | **BLOCKER: VERIFY ITEM/CAPTURE RIGHTS OR REWORD UNSUPPORTED ITEM-SPECIFIC CLAIM BEFORE RELEASE**. |

### Citable source URLs (the source locations, not automatically a license for reuse)
- NASA Brand Center: https://www.nasa.gov/nasa-brand-center/
- NASA Apollo 1 photo: https://www.nasa.gov/image-detail/apollo-1-crew-honored/
- NASA Apollo 204 report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
- Franklin Wikimedia Commons file + license: https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg
- NYPL exact item: https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0
- NYPL mapped history/source identification: https://libguides.nypl.org/nyc-rail-transit/companies and https://libguides.nypl.org/nyc-rail-transit/brt
- NYPL public-domain/rights policy: https://qa-digitalcollections.nypl.org/about
- NYPL capture-level API rights guidance: https://api.repo.nypl.org/

## Non-negotiable release constraints
- This branch is stacked on #613, isolated from Apollo #158 and Mind #171; frozen #49 unchanged. It does not replace the published page 6, modify themes/settings/navigation, deploy, or merge.
- WordPress.com Personal does **not** provide a free native staging clone. The authenticated local Playground is not a WordPress.com Atomic host replica. No upgrade/subscription is proposed.
- Production still has **72 Margins records**, Jetpack subscription and both Focus Fieldbook links. Do not overwrite, remove, or sync subscriber data. Confirm current counts immediately before any separately authorized release.
- The founder has not selected a final art direction or provided a production release authorization. Independent exact-head QD, historical image item-level rights, visual/manual AT review, mobile Lighthouse and WordPress.com hosted parity are still open.
