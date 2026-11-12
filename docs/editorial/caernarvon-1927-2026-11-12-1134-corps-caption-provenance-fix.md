# Caernarvon 1927 — verified Corps-caption provenance correction and release handoff
Date: November 12, 2026, 11:34 Pacific. Investigation: existing WordPress **DRAFT #2151**, [owner issue #1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463). This is an editorial audit, **not** a publication approval.

## Problem established before editing
The draft attributed the exact phrase **“With MRC approval”** to an *earlier* Corps spillway brochure (operation figures through 2014). The wording of that earlier version had **not** been directly verified in an original edition. The **December 2018** New Orleans District *Bonnet Carré Spillway* booklet was previously checked in extracted source text and contains **both** that phrase and **“saved the city”** in **one caption**. These are **one institutional source lineage**, not two independent Corps findings.

- Official 2018 USACE booklet: https://www.mvn.usace.army.mil/Portals/56/docs/Recreation/BCS/Brochures/BC%20spillway%20booklet%20Dec%202018%20.pdf (previously extracted caption text, lines 134–144; indexed source search also returns both short phrases).
- Leland R. Johnson, *Situation Desperate* (USACE, 2011), [government-published PDF](https://www.govinfo.gov/content/pkg/GOVPUB-D103-PURL-gpo27158/pdf/GOVPUB-D103-PURL-gpo27158.pdf), printed pp. 151–153. Johnson reports Jadwin and the Mississippi River Commission raised **no objection**, while the Corps would neither issue a permit nor carry out the demolition. This is an institutional history citing 1927 records, **not** the original 1927 MRC vote or letters.
- Earlier USACE brochure: https://www.mvn.usace.army.mil/Portals/56/docs/PAO/Brochures/BCspillwaybooklet.pdf (retained in bibliography **only**, explicitly flagged as not inspected to establish exact corresponding caption wording).
- The unofficial AnyFlip transcription is not controlling evidence, original-edition authentication, or image-rights clearance.

**Interpretation:** A 2018 caption's “With MRC approval” cannot be promoted to proof of a formal federal permit; “saved the city” is likewise an institutional retrospective, not a measured hydraulic counterfactual.

## Controlled WordPress corrections
- **Block #15, core/paragraph:** replaced the unverified earlier-edition citation with the verified December 2018 official booklet; explains that the two phrases belong to **one retrospective caption**. All surrounding federal-role discussion remains.
- **Block #79, core/list, Sources & Further Reading:** corrected edition and quotation provenance, retained the earlier official edition with an **unverified exact-caption** caveat, and clarified that a third-party transcription is neither edition authentication nor rights clearance.
- Used WordPress **optimistic single-section locking**; no other blocks or templates were rewritten. Both writes returned **no content warnings** and were independently read back.

### Fresh authenticated post snapshot
- WordPress local modified: **2026-11-12T11:34:20**.
- Current Gutenberg SHA-1/section content hash: **6b06724152de158fc3e94d40fae2c6b46395a383**, superseding the 07:43 revision e89879d2b34a53de75d04f2a92bbab832de5aaf3.
- **DRAFT**, never published; **81 top-level Gutenberg blocks**, **42 bibliography entries**, **four** locally hosted NOAA/Library of Congress photos, **two** existing original evidence graphics, featured image ID **2148**. Structural audit: 149 hyperlinks to 58 unique destinations.
- WordPress meta values: **_jetpack_dont_email_post_to_subs=true**, **jetpack_publicize_feature_enabled=false**, **jetpack_post_was_ever_published=false**.
- All four authenticated media records (2148, 2255, 2202, 2149) retain FV-local URL, alt text, caption and dimensions; this is **metadata only, not browser rendering**.
- The earlier USACE URL remains **bibliography only**, not the source of the exact quoted words in the main text.

## Read-only visual QA integrity
Updated both source-controlled inspector scripts to require the **new Corps 2018 caption-provenance sentence within a single paragraph**, in addition to the previously required same-paragraph USGS 2,470,000 / 2,472,000 ft³/s markers:

- docs/editorial/tools/qa_browser_console_2151.js
- docs/editorial/tools/inspect_wp_draft_2151.py

Each updated tool was independently fetched and checked after committing. **They have not been executed against an authenticated production-theme preview.** Source-text checks are not 390px/1440px screenshots, DOM/overflow evidence or ordinary-reader PDF verification. Playwright's --sha argument is declared metadata, not a cryptographic measurement of browser markup.

## Release gate still CLOSED
[Site QA #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589) must test **this latest draft**, not the 07:43 version: editor-authenticated current-theme screenshots at **390px and 1440px**, source/caption/alt rendering, ten-row scrollable comparison table, hierarchy and overflow. It also needs human-checked anonymous PDF page images for both Corps brochures and USGS sources, or verified claim-equivalent alternatives. Automated HTTP 403 is **not** proof of ordinary-reader failure. The 60 MB govinfo historical PDF supplied readable text, but the web screenshot service rejected it as too large; this is not a PDF-pixel PASS.

**Publication:** NO. **Homepage, shared templates, unrelated WordPress posts:** unchanged. **Subscriber emails, auto-social, Grok distribution:** none. **Additional paid services:** none.

### Next concrete action
Site QA must provide dated PASS/FAIL evidence at both viewports for the exact **6b067241...** revision and address document-reader access. The Investigations lane can publish only after a final source, image-rights and responsive QA pass, with email suppression and auto-social disabled on the first publish request and an independent post-publication readback.
