# Verified P0 source relocations — November 5, 2026

**Isolated media-only draft.** No homepage work, Site QA #154 edits, existing Media PR #183 edits, WordPress writes, third-party image downloading, caching, or subscriptions.

Two original sources remain unconfirmed as visitor-browser failures, but each now has a **retriever-rendered same-topic, same-named publisher source**. See [two-row JSON](../qa/media-recovery/p0_source_relocations_20261105.json) and fail-closed validator/test.

| Published slot | Published original | Web retriever of old URL | Candidate image rendered by independent web retriever | Publication |
| --- | --- | --- | --- | --- |
| 287:5 — Sunshine Skyway | https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg | Wrapper **404** | https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg | **HOLD** |
| 418:2 — Scotch Cap | https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg | Wrapper **403** (earlier audit) | https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg | **HOLD** |

**Specific visual-integrity discovery:** Skyway's stored ALT claims “the later bridge replacement” is depicted. The retrieved same-publisher image shows the ship and collapsed **1980 original bridge**, not the later replacement bridge. The April 10, 2020 publisher page (https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/) credits **University Press of Florida**, not FV. No license to mirror, hotlink indefinitely or re-publish has been established. The original binary and image pixel identity were not obtained or compared. Proposed output ≤960px only after original master geometry and rights verified; no invented dimensions.

**Scotch Cap:** The National Coast Guard Museum's October 30, 2024 article (https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/) credits the museum-rendered 600×463 photograph to **U.S. Coast Guard** and dates the event April 1, **1946**. Same `Scotch_Cap_debris2_1946` filename stem as the broken-source candidate, but exact binary identity unproved; never upscale the 600px rendition to 960px. NOAA's separate Scotch Cap debris image page (https://oceanexplorer.noaa.gov/multimedia/okeanos-explorations-seascape-alaska-ex2304-features-geology-media-lighthouse-debris/) incorrectly labels similar aftermath as “following a **1964** tsunami”; don't import the caption/date. Item-level rights, attribution and CMS approval remain **HOLD**.

**Release sequence:** Site QA #154 captures logged-out desktop/mobile original `currentSrc`, request ID, actual response and `naturalWidth/Height`, screenshot and cold transfer bytes. Media recovery then documents exact candidate identity, publisher permission/USCG rights, credit, no-upscale geometry, side-by-side visual review and caption accuracy. Only after separate approval prepare an explicitly reversible WordPress-media plan; never automatically rewrite Gutenberg blocks. Quantify the claimed 76% reduction using *paired browser transferred bytes*, not original WordPress stored bytes or a broken 0-byte baseline.

**Frozen sitewide context (not a fresh production census):** 61 posts; 355 source references; 288 external-origin references under Media #183 classifier; 13 WordPress originals >1.5 MiB total 43,522,829 **stored** bytes. The 42 alleged broken references remain browser-unverified; the 76% weight-reduction claim remains unmeasured; **production media repairs: zero**.

Tests: `node --test qa/media-recovery/test_p0_source_relocations_20261105.cjs` and `node qa/media-recovery/validate_p0_source_relocations_20261105.cjs qa/media-recovery/p0_source_relocations_20261105.json`.
