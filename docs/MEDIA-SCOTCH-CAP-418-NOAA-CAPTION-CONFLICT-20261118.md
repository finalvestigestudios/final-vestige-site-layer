# Scotch Cap post 418 — provenance, rights and chronology HOLD

**Checked:** 2026-11-18 01:23 PST. **Scope:** read-only Media Recovery PR #2747; Site QA PR #154 owns logged-out Chromium checks. No homepage visuals, production WordPress writes, image downloads or mirrors.

## Two priority external image slots

- **418:1 Coast Guard portrait:** exact published Jetpack and media.defense.gov origin in the [machine ledger](../qa/media-recovery/scotch_cap_418_provenance_20261118_0123pst.json). The [USCG official record](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) uses **VIRIN 210330-G-DE713-0002.JPG**, identical to the authored origin filename. It advertises approx **0.04MB** and explicitly labels the photo *public domain, cleared for release*, with credit and DoD restrictions concerning recognizable persons, emblems and endorsement. This is **catalog/filename concordance**, not binary/crop identity; master pixels and SHA-256 unknown, proposed output geometry held.
- **418:2 destroyed lighthouse:** the published original is https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg. The [National Coast Guard Museum](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/) offers a similarly named **600×463 preview**, 5_-Scotch_Cap_debris2_1946-600x463.jpg. Filename stem and subject do **not** certify pixel/crop identity or republication rights. If the preview is ever licensed and used, **do not upscale to 960px**; max from this preview is 600×463.

Both originals had HTTP **403 in an independent public retriever** on November 17 at 18:32 PST, **not proven guest errors**. On November 18 the exact Jetpack proxies were inaccessible to the public reader, with **no numeric HTTP status**. Guest-browser GET/decode/dimensions/bytes remain **unknown**.

## Important new authoritative metadata discrepancy

Two NOAA Ocean Exploration individual image cards for the [Scotch Cap lighthouse](https://oceanexplorer.noaa.gov/multimedia/okeanos-explorations-seascape-alaska-ex2304-features-geology-media-lighthouse/) and [its debris](https://oceanexplorer.noaa.gov/multimedia/okeanos-explorations-seascape-alaska-ex2304-features-geology-media-lighthouse-debris/) say the tsunami occurred in **1964**. That conflicts with NOAA's own [expedition parent article](https://oceanexplorer.noaa.gov/expedition-feature/okeanos-seascape-alaska-ex2304-features-geology/), [1946 tsunami dataset](https://sos.noaa.gov/catalog/datasets/tsunami-historical-series-aleutian-islands-1946/), and [USCG disaster history](https://www.history.uscg.mil/Browse-by-Topic/Assets/Land/All/Article/1988680/scotch-cap-light/), which confirm **April 1, 1946**. **Do not inherit NOAA image-card dates automatically** when sourcing or staging replacements. This is a *metadata* contradiction, not proof of wrong photographs.

**Surname ambiguity:** the USCG photo caption identifies *Anthony Pettit*; its official [site roster](https://www.history.uscg.mil/Browse-by-Topic/Assets/Land/All/Article/1988680/scotch-cap-light/) lists *Chief Boatswain Anthony L. Petit*, matching the FV alt. Official sources conflict. **Do not automatically change ALT**; refer historical spelling to editorial research.

## Conditional WordPress staging and cold-byte acceptance

1. Site QA's **existing** guest Chrome desktop/mobile collector checks exact currentSrc, redirects, final numeric HTTP GET/MIME, decoded body raster dimensions and SHA-256, img.decode(), screenshot and unique cold transferred bytes. Tool-blocked 403 is not a visitor 403.
2. For a confirmed broken slot, acquire exact frame/crop from a licensed primary master, record authoritative rights/credit (including DoD caveats), SHA-256 and true native pixels; no unlicensed scraping or circumvention. Derive proportional width = min(960, native width) **without upscaling**, with visual proof and responsive WordPress sizes.
3. Only after separate approval, use an isolated **nonproduction WordPress** media item and reversible slot manifest (post ID, old src/ALT/caption, new staging media ID, hashes, transfer bytes and rollback). No raw Gutenberg rewrites, homepage edits or live publishing.
4. Compare same viewport/DPR cold before/after screenshot identity, decoded slots, unique HTTP response-body transfer bytes, LCP and CLS. The reported **76% saving** is not evidenced by stored-library originals.

**Limits:** historical 61/355/288 and recent 66/361/294 are separate snapshots; **42 alleged broken images remain guest-unconfirmed**; **20 originals over 1.5MB** total **64,385,752 stored bytes**, not visitor downloads. The adjacent Node validator and 22-case native regression suite are offline safety gates, not HTTP/rights/binary proof. **Release: HOLD**. Zero WordPress production writes, rehosts, downloads, merges, deployments, homepage changes or charges.
