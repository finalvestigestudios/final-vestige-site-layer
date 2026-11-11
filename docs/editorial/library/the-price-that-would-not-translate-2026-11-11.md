# The Price That Would Not Translate — Historical purchasing-power source witness

**Owner:** Final Vestige Studios Library Resource Studio  
**Research/primary-source review:** 2026-11-11 (Pacific)  
**Disposition:** Complete local release candidate. **PUBLICATION HOLD**.

## Reader need and difference from existing resources

Readers encounter a historical cash price and ask what it was worth, how expensive the item really was, or whether a family could afford it. These are three different questions. This guide teaches a precise CPI adjustment and keeps commodity, wage, location, quality, scarcity and household constraints separate. It complements the already-published *The Open Account* (ledger transactions), *The Second Currency* (wartime ration authorities) and *The Archive Trail* (source provenance). GitHub issue searches for historical prices/CPI/purchasing power and WordPress pages searches for price/inflation found no dedicated equivalent. It does not alter Preparedness, Investigations, homepage code or their assets.

## What was completed (local conversation release package)

- **The_Price_That_Would_Not_Translate.html**: self-contained illustrated field guide, accessible three-branch original SVG evidence diagram, seven-pass method, interactive on-device purchasing-power witness desk, 14 selected annual CPI benchmark years (1913–2025), editable index fields, locally downloadable JSON source witness, print style, 10 official sources and relevant FV cross-links. No external JS, tracking or data submission.
- **Price_Witness_Research_Cards.pdf**: original 4-page illustrated, printable US Letter field cards with provenance worksheet and 10 clickable institutional links.
- **Price_Source_Provenance_Rights.csv**: 13 dated source, evidence-scope, qualification and reuse/access records.
- **Benchmark_CPI_Annual_Selected_Years.csv**: 14 chosen rounded annual values, with source, date and limitations.
- **MANIFEST.json**, **QA_REPORT.json**, **SHA256SUMS.txt**, and **FV_Price_Witness_Release_Candidate.zip**; attachments to this Library Studio run, *not* currently WordPress-hosted or GitHub binary attachments.
- Final ZIP SHA-256: `ab1df4924243fc137ab11683eeead3df5a557df61f2732cbcbc7f2932626a5e1`. HTML SHA-256: `26e82cac94bef3e03a19c665846f92c205b8b58257e25a0d0b54af6c8fbaf175`.

## Primary institutional sources, checked 2026-11-11

1. [Federal Reserve Bank of Minneapolis — CPI 1913–present](https://www.minneapolisfed.org/about-us/monetary-policy/inflation-calculator/consumer-price-index-1913-): formula and *rounded annual* data. Presets **1913 9.9, 1920 20.0, 1930 16.7, 1940 14.0, 1950 24.1, 1960 29.6, 1970 38.8, 1980 82.4, 1990 130.7, 2000 172.2, 2010 218.1, 2020 258.8, 2024 313.7, 2025 321.9**. **2026 is provisional, intentionally excluded**.
2. [BLS — Purchasing power and constant dollars](https://www.bls.gov/cpi/factsheets/purchasing-power-constant-dollars.htm): annual CPI ratio.
3. [BLS CPI Inflation Calculator](https://www.bls.gov/data/inflation_calculator_inside.htm): annual-average convention.
4. [BLS CPI history](https://www.bls.gov/opub/hom/cpi/history.htm): index revisions and early coverage.
5. [BLS CPI FAQ](https://www.bls.gov/cpi/questions-and-answers.htm): household, geographic and basket limitations.
6. [BLS CPI quality adjustments](https://www.bls.gov/cpi/quality-adjustment/): product substitutions.
7. [BLS CPI concepts](https://www.bls.gov/opub/hom/cpi/concepts.htm): exclusions (including investment housing purchases).
8. [BLS — A Century of Price Change](https://www.bls.gov/opub/mlr/2014/article/one-hundred-years-of-price-change-the-consumer-price-index-and-the-american-inflation-experience.htm): historical interpretation.
9. [BLS — National Compensation Survey history](https://www.bls.gov/respondents/ncs/history.htm): archival wage-research starting point.
10. [Census — Historical Household Income](https://www.census.gov/data/tables/time-series/demo/income-poverty/historical-income-households.html): independently sourced household income; years and definitions vary.

**Numerical check:** *fictional* 1920 boot price $5 × (321.9/20.0) = $80.475, displayed **≈$80.48** in 2025 broad purchasing power. Neither contemporaneous item price nor affordability. 1913 $1 to 2025 = $32.52 with rounded benchmark indexes. Never claim actual shoe costs or wages from CPI.

## Rights and accessibility

All page text, original SVG, diagram, PDF workbook, code and fictional worked example are original Final Vestige material authored 2026-11-11; no third-party photographs, archival scans, institutional logos, historic advertisements or table layouts are reproduced. Numerical CPI facts are attributed. All institution records are linked, and rights/access require per-item review. The original SVG has a title, long description, caption, and visible **FICTIONAL** label.

Source field names, form labels, validation messages and live calculator output are accessible text. Keyboard focus, responsive layout and no-script access to substantive article were tested locally. Data remains in-browser until explicitly exported; invalid/non-HTTPS research URL exports are blocked.

## QA — important scope boundary

Standalone HTML injected into headless Chromium at **320, 390, 768 and 1440px**, with JS enabled/disabled: **8/8 PASS**, zero page-wide horizontal overflow and zero JS errors. Functional tests: example $80.48, 1913 $32.52, zero-index refusal, reset, unsafe URL refusal, local JSON download, witness clear — **7/7 PASS**. Screenshot previews at 390/1440 and four PDF page renders inspected; PDF contains embedded clickable sources; ZIP CRC PASS.

**THIS IS NOT A WORDPRESS PRODUCTION-THEME QA PASS.** The WordPress screenshot-link connector returns mshots URLs but no inspectable pixels in this execution environment, and container DNS blocks public and screenshot hosts. A subset of public FV pages returned HTTP 429 to web fetching; a denied automated request is not proof of a broken public link. No claim of an all-source ordinary-browser pass.

## Publication HOLD / exact next actions

1. In an authorized browser, inspect *actual FV-theme preview* at 320/390/768/1440, keyboard/filter, print, document scrolling, popup interaction and representative reference links. Fix any preview issues.
2. Verify suppressions for first-publication email and Jetpack Social; connector currently cannot set `_jetpack_dont_email_post_to_subs=true` or `jetpack_publicize_feature_enabled=false`. **Do not publish through an interface that cannot enforce required suppression.**
3. Host the PDF and standalone calculator under verified public resource URLs (or embed tested, scoped markup).
4. Publish an appropriately named Library child page only after all gates pass; use noindex while draft, then remove noindex. Minimal corresponding Library card and relevant related-guide links.
5. Independently check anonymous URL, canonical/SEO, download response, links/media rights, responsive behavior and no subscriber/social activity.
6. A future Grok short could compare a 1920 price with CPI and a worker's wages, showing the difference; **promotion only after public URL verified**. Do not modify Grok accounts here.

The **higher priority** remains in-place Research Sources #1338 correction under [#1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788). Do not publish a duplicate 90-source directory or edit staging #2354. No public WordPress edits, emails, social posts, spending or other editorial lane changes occurred.
