# Bohemia investigations — FY2000 original-page verification and WordPress staging audit
**Date:** November 14, 2026 (Pacific). **Disposition:** draft only; DO NOT PUBLISH. **Agent scope:** Investigations, not shared templates, homepage, other editors' posts or social.

## Coordination and duplicate review
- Live [Journal](https://finalvestige.com/blog/) inspected November 14, 2026: 66 published investigations indexed in the page (newest date November 2), no Bohemia companion in the targeted results. [Editorial Standards](https://finalvestige.com/editorial-standards/) checked in live HTML and authenticated page record. The site policy requires original records, qualified uncertainty, documentary-image credits and correction transparency.
- WordPress authenticated published/draft search for "Bohemia" found no existing Bohemia post; the only matching draft was unrelated **Caernarvon #2151**. It was not edited. GitHub repo `finalvestigestudios/final-vestige-site-layer` and Investigations coordination issue [#1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463) inspected before work. No homepage or theme edits.

## Primary-source visual verification completed
**Source:** State of Louisiana, *Comprehensive Annual Financial Report for the Year Ended June 30, 2000*, Note 16: Contingencies, **printed p. 67**, **zero-based PDF image 73**. [Official original PDF](https://www.doa.la.gov/media/xcem4e3d/cafr2000.pdf).

Searchable text and the **original PDF page screenshot itself** were independently examined on November 14. The page explicitly reports:
- Orleans Levee District was defendant or co-defendant in **73 lawsuits**, **26 related to the Bohemia Spillway**.
- The district's own financial statements carried **$2,429,293 in liabilities for its claims and litigation collectively**.
- Claim types included damages, possession of property and contract disputes.

**Limitations:** no unique docket inventory for the 26 matters was supplied; no support for assigning the $2,429,293 specifically to Bohemia, subtracting it from the Vogt judgment, or treating it as a beneficiary payment/current balance. The previous screenshot/403 hold **for this particular FY2000 page** is cleared. The separate **2015 flood-authority minutes PDF** was directly reopened as text, but screenshot calls for its printed pp. 24–25 continued to fail; that visual hold remains.

## Reader manuscript
Updated [reader edition](./bohemia-spillway-reader-edition-2026-11-14.md) to **v8**: corrected the FY2000 passage, entry [19] and the original litigation graphic's release register to distinguish a now-inspected original source image from still-unverified WordPress production rendering. Commit: `56e1f816ce428e1fb68bcd55a5f87d143db242b3`. The full [60-source dossier](./bohemia-spillway-2026-11-12-land-roster-rights-claim-investigation-draft.md) was preserved, without new claims of final payments.

## Authenticated WordPress staging
**New investigation draft:** WordPress post **#2488**, *The Spillway That Kept Its Names*, slug `the-spillway-that-kept-its-names-bohemia`. Draft entry [here](https://finalvestige.com/?p=2488) (not a public article). A **new post** was staged because the authenticated post search found no Bohemia draft; Caernarvon #2151 was not reused or modified.

The staging conversion created **92 top-level Gutenberg sections** verified through the independent WordPress block-section listing: **76 paragraphs, 12 headings, 2 images, 1 native original infographic HTML block and 1 20-entry bibliography list**. The draft's body was independently re-read after the update. Categories: **Discovery (9369)** and **Ingenuity (232815)**. Featured documentary image: WordPress **#2484**.

**Documentary images, locally hosted:**
1. WordPress **#2485**, 2007 USDA NAIP aerial view prepared for NASA Earth Observatory, alt and dated credited caption present.
2. WordPress **#2484**, 2023 USGS Landsat 8 view prepared for NASA Earth Observatory, alt and dated credited caption present.
Both item metadata and original local WordPress media URLs were retrieved through authenticated media reads.

**Original diagram embedded:** Source-derived HTML/CSS, captioned and keyboard-readable, titled *Twenty-six cases among seventy-three*. It shows 26/73 Bohemia-related cases and 47 other cases, explicitly distinguishes the collective $2,429,293 litigation liability, and cites the official FY2000 p. 67. It uses no external image hotlink, generative historical reconstruction, remote CSS or paid service. SVG originals for other manuscript figures remain in GitHub and were **not** embedded in WordPress until locally cleared.

**Automation/email/social controls**, returned and independently read back from WordPress:
- `status=draft`
- `_jetpack_dont_email_post_to_subs=true`
- `jetpack_publicize_feature_enabled=false`
- `jetpack_seo_noindex=true`
- Current draft site-local modified timestamp after visual insertion: **2026-11-14T09:44:40**.
- Full 20-source bibliography items present with internal anchor IDs; all two image block IDs re-read. Post ID and metadata verified, not inferred from API success.

## Publication holds
1. Original signed *Vogt* July 24, 1998 allocation judgment, the court-filed 1997 accounting exhibit and related payment/satisfaction records; final claimant-level balances cannot be asserted.
2. Original *Haspel & Davis* state consent judgment and beneficiary ledger, and execution/amount of the 2015 escrow transfer; these cannot be merged with *Vogt*.
3. Original 2015 flood-authority meeting minutes still lack direct page screenshot due to source retrieval restriction, though official text was reopened; obtain alternate official copy.
4. Legal and structural human editorial pass; scrub remaining production language from bibliography; check every source URL, caption/credit and final claims in actual draft HTML.
5. Authenticated **390px and 1440px WordPress draft/production-theme screenshot inspection** is not provided by the current read connector. Block parsing is not visual QA; the new HTML/CSS figure and photography require final in-theme review.
6. Original SVGs need rights-cleared local publishing assets and final layout QA if selected. No subscriber mailing or social distribution before explicit editorial release.

**Outcome:** new source image checked; reader corrections committed; full draft created, sourced, visually staged and independently read back; release **held** with explicit blockers. **No public article, homepage/template edit, subscriber email, social post, or new paid service**.
