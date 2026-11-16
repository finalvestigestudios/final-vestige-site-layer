# Bohemia Spillway — reader v44 structural editorial and release audit

**Date:** 2026-11-15, approximately 20:35 Pacific. **Owner lane:** Investigations only. **Status:** HOLD — WordPress draft #2488; nothing published or mailed. **Public URL:** None. **Editor URL:** https://finalvestige.com/wp-admin/post.php?post=2488&action=edit

## Coordination and scope
Read current public [editorial standards](https://finalvestige.com/editorial-standards/), [Journal](https://finalvestige.com/blog/), WP post queue, existing [Investigations #1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463) and [production QA #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589) before editing. No duplicate Bohemia post created. Other investigations, the Caernarvon draft #2151, homepage, templates, navigation, and shared pages were not modified.

## Evidence rechecked (not a new discovery)
- [Louisiana Fourth Circuit, *Succession of Ursin/Eusan v. Board of Levee Commissioners*, No. 2011-CA-1105, 2012-09-26](https://law.justia.com/cases/louisiana/fourth-circuit-court-of-appeal/2012/2011-ca-1105.html): court narrates 2005 Tract 78 conveyance and adjudicates revenue and interest separately. Court outcome is not a cleared-payment register. The opening previously vetted this source; no 2026 claimant payment asserted.
- [Southeastern Louisiana University's *Rod Lincoln Collection* finding aid](https://www.southeastern.edu/acad_research/programs/csls/historical_collections/archival_collections/l_m/lincoln_rod/): indexed *Times-Picayune* notice (1987-02-21), $175 challenge headline (1988-10-08), and *Plaquemines Gazette* settlement headline (2000-12-15). This turn verified the institution's indexed catalogue entry through search, NOT the original clippings or any payment.
- [NASA Earth Observatory, *Mardi Gras Pass*, 2023-02-21](https://science.nasa.gov/earth/earth-observatory/mardi-gras-pass-150986/): current credited image/source details checked; 2007 NAIP and 2023 Landsat images describe the landscape, NOT cadastral boundaries of Tract 78.
- Continuing court source [16] supports the separate March 31, 1999 ruling in the existing dossier. This edit reorganizes its placement and improves the distinction between statutory accounting duty, judicial remedy, and payment. No new legal opinion attributed or quotation invented.
- [Editorial standards](https://finalvestige.com/editorial-standards/) require primary sourcing, explicit evidentiary limits, source credits, and labeling of reconstructions.

## Edit actually staged
Moved two Gutenberg paragraphs about the March 31, 1999 ruling and its statutory-remedy caveat out of the opening of `The accounting was already required` and placed them after the 1984 accounting obligation, 1996 *Riley* access proceedings and 1997–99 *Vogt* accounting discussion. Replaced generic introductory copy with an explicit 1984 Section 3 opening and clarified the separate 1999 ruling. Added one source-caveated university finding-aid paragraph immediately BEFORE its existing original studio graphic. Removed four redundant bridge paragraphs in the judgment, 2014 settlement-offer, financial-classification and conclusion passages; none contained unique claim-level evidence. **This is a narrative/structure pass, not a new accounting discovery or complete manuscript abridgment.**

WordPress guarded per-block actions used optimistic `modified`, serialized `content_hash`, target `block_hash`, and verified target type; all substantive modifications targeted post #2488 only. An intermediate insertion position was corrected by moving the new paragraph to the intended position before the archive graphic, then re-read. All changes are reflected in the final readback. Canonical [reader manuscript v44](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/main/docs/editorial/bohemia-spillway-reader-edition-2026-11-14.md) was updated, including a correction to its stale opening bibliography count: **55 selected entries / 84 master evidence entries**, not 54/83. It is not a byte-identical Gutenberg export; use WP readback for exact published-surface verification.

## Independent WP release readback (post edit)
- Target **post 2488**, status `draft`, site-local `modified=2026-11-15T20:35:28`.
- Top-level Gutenberg blocks **246** (previously 249). Serialized content SHA-1 from authenticated WP section listing **`48e7290728f5085b67ab0243f928e0cc1c5aadae`**.
- Raw WP content: **224,657 characters**; automated stripped token estimate ~21,900 words (includes substantial source bibliography and graphics; this is not a polished reader-body word count).
- Reader source-list targets **55**, all unique; **234** same-post citation links; 55 unique referenced IDs, **zero unresolved targets, zero unreferenced source IDs, zero duplicate IDs**.
- Categories remained **9369, 232815**; featured media remains **2484**.
- Jetpack **`_jetpack_dont_email_post_to_subs=true`**, **`jetpack_publicize_feature_enabled=false`**, **`jetpack_seo_noindex=true`**, `jetpack_post_was_ever_published=false`. No publish action.
- Media **#2484**: NASA Earth Observatory/Joshua Stevens, February 13, 2023, USGS Landsat 8, 1280×1280 JPEG, 302,285 bytes as reported by WP media metadata, alt/caption/source present.
- Media **#2485**: USDA NAIP September 20, 2007 via NASA Earth Observatory/Joshua Stevens, 1125×1280 JPEG, 440,401 bytes as reported by WP media metadata, alt/caption/source present.
- Local metadata and on-page block attributes support attribution but DO NOT prove anonymous public image-byte fetch or actual displayed captions.
- Existing original first-party figures retained; no new AI reconstruction, copyrighted scan, external image hotlink, social media item or paid service.

## Release blockers (FAIL/UNKNOWN; do not publish)
1. **Visual QA:** actual editor-authenticated current WordPress theme screenshots/DOM overflow/mobile typography at **390px and 1440px of this exact SHA** were not accessible. An unauthenticated screenshot endpoint or media API success is not a visual pass.
2. **Public image bytes:** direct container requests for both published JPEG source URLs returned `Could not resolve host: finalvestige.com` (DNS failure); this says nothing definitive about what a normal public visitor sees. Need independent anonymous 200 OK JPEG byte/alt/caption proof.
3. **Substantive financial/legal:** signed FY2014 case-specific settlement instruments, accounting schedules/journal entries, 1997 *Vogt* exhibits, court-registry disbursement orders, and claimant/payee receipts remain outstanding. Claims of universal payment, no payment, or a current unpaid total are unsupported. Final independent legal/editorial review also pending.
4. **Long-form readability:** 246 Gutenberg blocks remain; continue substantive condensation of the already researched material, but do not silently discard source nuance or replace the published-source bibliography wholesale.

**Release decision:** HOLD as unpublished WordPress draft. **New spending:** $0. **Emails/social:** none. Grok's separate distribution lane should not launch until an independently verified public URL exists.
