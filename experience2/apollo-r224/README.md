# Apollo Evidence Atlas R224 — ChronologyRail period custody (staging only)

Isolated child of [draft PR #1642](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1642) under [Experience 2.0 Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), conversion governance [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) and [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). **No merge, deploy, WordPress write, creator publication or commerce activation.** Do not change frozen homepage PR #49 or independent Research Desk PR #158.

## What changes

The existing ChronologyRail has four dated milestones (NASA photo capture dates 1966-10-18 and 1967-01-03, the 1967-01-27 accident, and 1967-01-28 aftermath capture). R224 adds a fifth **April 1967** *Review Board report completion* record, with a NASA source link, explicit month-only precision and a native link back to the SourceDrawer. A visible, accessible date-type key distinguishes photograph capture, accident and retrospective report dates. It adds no invented event time, map pin, photo, JavaScript, tracking, signup, merchant, or additional CTA. The single original investigation link remains free and unchanged.

The primary retrospective report supports probable electrical arc but does not determine the specific ignition source: [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). NASA's [Apollo 1 Resources](https://www.nasa.gov/apollo-1-resources/) says the final report was completed in **April 1967**, without a precise completion day. The original NASA image catalog sources stay in R223. Separate [NASA advertising guidelines](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) do not confer promotional rights merely because source URLs are cited. No media has been embedded or relicensed.

An additional `chronology-period-custody.json` file records date precision, report source, no geo, no rights certification, no verified creator asset and no approved paid offer. PHP now SHA-pins the ledger and altered HTML/CSS, returning the **free original article** on tampering.

## Exact local replay

Requires a generated R223 staging distribution with parent manifest SHA-256 `60e3bcd4201715a769d1e4d819dfc4d09498eeace5e8193a535fae7350ef840e`, Python, PHP CLI, Playwright for Python and `/usr/bin/chromium`.

```sh
python experience2/apollo-r224/build_r224.py --parent /path/to/generated-r223-dist --target /tmp/apollo-r224/dist
python experience2/apollo-r224/qa/chronology_rail_browser_gate.py --parent /path/to/generated-r223-dist --builder experience2/apollo-r224/build_r224.py --out /tmp/apollo-r224/qa
```

**R224 exact generated manifest SHA-256:** `f739b70ced7c93254f69b9d58e1463a97d4288780202622b74d2be50431a57ea`.

On Nov 8, 2026, the exact committed builder and QA source were executed twice, 14 browser contexts per run across 320, 360, 390, 768, 1024, 1440 and 1920 px (JavaScript on/off), plus forced colors/reduced-motion contexts. PHP normal/print/late, deliberate ledger corruption fail-open, four EvidencePlates, five chronology entries, date key, NASA report link, keyboard/touch/native disclosures, anchor integrity, printable source evidence, canonical single 44px+ free CTA, no active content, no invented geo and no horizontal overflow **PASS**. Fourteen screenshot hashes matched across runs. Chromium uses `page.set_content` on actual PHP-rendered HTML/CSS because local HTTP navigation is restricted. These are offline staging observations, **not** installed WordPress or production Core Web Vitals.

**Outstanding release blocks:** inherited R198 canonical-source ancestry discrepancy; genuine axe-core (unavailable offline), NVDA/VoiceOver, desktop browser zoom, installed WP/Assembler lifecycle and CSS acceptance, exact-head hosted CI, independent QA and founder authorization. No live performance or paid transaction evidence.

## Conversion contract

Flagship = Apollo 1 for prospective Grok long-form/Shorts; publication asset_id, post URL and UTMs are **not verified**. Trust hypothesis: clearly dating retrospective evidence reduces reader confusion before a single relevant free long-form investigation CTA. This is not a revenue claim. The educator dossier remains hypothetical, **not a live SKU**. Do not insert unrelated affiliate commerce into a fatal-accident narrative. A later rights-cleared, available product can be evaluated separately for qualified buyers. Metrics require creator asset `utm_content`, human sessions, actual CTA interactions and independently confirmed paid orders/commissions less refunds and fees, on seven- and thirty-day cohorts; a click or signup is never a sale. Grok owns content/distribution, Praxxis external review, Claude production engineering, and founder release/spend approval.
