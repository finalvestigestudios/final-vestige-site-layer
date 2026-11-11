# The Color Was a Key — telescope color composites and source-trail method

**Owner:** Final Vestige Studios Library Resource Studio  
**Source review:** 2026-11-11  
**Release state:** LOCAL ARTIFACT READY; WORDPRESS PUBLICATION HOLD  
**Theme:** Scientific-image literacy / filters / archival science provenance. Distinct from the existing photographic identification, scanned-image comparison, image licensing, patent, and map methods.

## Reader problem / editorial claim

Telescope imagery often visualizes radiation outside the visual spectrum. A display palette can encode measured bands or intensity without claiming to reproduce naked-eye appearance. The correct evidence question is whether an image record preserves the instrument, exposure date, band/filter mapping, image-processing credit, limitations and link to calibrated science data. Avoid the unsupported inference that representative color means fraudulent imagery, and the opposite unsupported inference that the displayed colors alone establish temperature, gas density, composition or distance.

## Completed local files

- **The_Color_Was_a_Key.html** — self-contained ~1,725-word original article; SVG three-stage source→detector→display explanation; interactive **fictional** three-channel color-composite laboratory with RGB contribution sliders; 14-field local-only JSON witness card; 12 linked sources. No remote scripts or embedded institutional images.
- **Telescope_Color_Key_Field_Card.pdf** — original four-page illustrated printable method/worksheet; four pages rendered and visually reviewed; 10 embedded source links.
- **Source_Provenance_and_Rights.csv** — dated claims, links, credit/use qualifications for 12 sources.
- **QA_REPORT.md**, **README.md**, regression test and integrity-checked release ZIP (saved in originating Library Studio run).
- ZIP SHA256 starts **f5e490777ada409c21ec**.

## Sources / critical details (linked, not copied)

1. [NASA: How Are Webb’s Full-Color Images Made?](https://science.nasa.gov/mission/webb/science-overview/science-explainers/how-are-webbs-full-color-images-made/) — infrared filter layers and chromatic assignment, not visible-light observation.
2. [NASA: Pillars of Creation (NIRCam compass)](https://science.nasa.gov/asset/webb/pillars-of-creation-nircam-compass-image/) — six-band legend; object and processing credit.
3. [NASA: Pillars of Creation (MIRI compass)](https://science.nasa.gov/asset/webb/pillars-of-creation-miri-compass-image/) — F770W, F1130W and F1500W map to blue/green/red.
4. [NASA: Webb First Deep Field NIRCam compass](https://science.nasa.gov/asset/webb/webbs-first-deep-field-nircam-compass-image/) — NIRCam observation 2022-06-07, press-image release 2022-07-11, six filters.
5. [NASA: L1527 MIRI compass](https://science.nasa.gov/asset/webb/l1527-and-protostar-miri-compass-image/) — three-band MIRI color key.
6. [Chandra: Adding Color to Chandra Images](https://chandra.harvard.edu/photo/false_color.html) and [X-Ray Images 101](https://chandra.harvard.edu/edu/xray101/false.html) — X-ray energies and intensity represented through chosen colors.
7. [MAST JWST archival data-products landing](https://archive.stsci.edu/missions-and-data/jwst) — distinguish raw, detector-corrected, flux-calibrated and combined data from outreach images.
8. [NASA Brand Center](https://www.nasa.gov/nasa-brand-center/) — no endorsement, emblem restrictions, some media includes third-party rights.
9. [ESA/Hubble licensing](https://esahubble.org/copyright/) — CC BY 4.0 for covered ESA/Hubble images, credit required; *not* a universal license to all Webb/NASA/Chandra imagery.
10. [FV Editorial Standards](https://finalvestige.com/editorial-standards/) and [The Archive Trail](https://finalvestige.com/the-archive-trail/) — internal evidence standards and cross-link.

All outside imagery was LINKED ONLY. Original FV vectors and mathematical fictional image arrays are the only art embedded. Illustration and interactive demonstration are explicitly labeled *synthetic, not calibrated, not actual telescope data*. Reuse rights must be resolved per original image record.

## Verification / release gate

- Standalone Chromium via Playwright HTML injection (file navigation denied by sandbox), 320/390/768/1440 × JavaScript on/off: **8/8 PASS**; no page-wide overflow or JS errors; 12 source entries, 14 labeled witness fields.
- JavaScript functional: composite canvas paints, red channel slider varies, reset restores, arbitrary text saved as inert JSON via download, form reset clears; all PASS.
- 4-page PDF rendered/visually reviewed; embedded institutional hyperlinks confirmed; release ZIP integrity PASS.
- **This is NOT a production WordPress theme visual pass.** Container DNS blocks actual public site and screenshot host, though WordPress mshots returns screenshot URLs; pixels unavailable here. Ordinary-browser external link checks and production keyboard/mobile/metadata verification remain required.
- First-publication mail and Jetpack Social suppression must be enforceable before WordPress creation/publication. Newsletter setting `email_new_posts_by_default=false` is known, but does not prove every custom action cannot email/share. Required `_jetpack_dont_email_post_to_subs=true` not exposed by current connector.
- **Decision: HOLD**. No public WP writes, no Library card additions, no media uploads, no subscriber/social actions.
- Publication P1 remains the correction of existing Research Sources page #1338 under [#1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788), without publishing competing #2354.

## Future promotion coordination

Potential Grok teaser after live publication: “Why does an infrared telescope image have colors? The image is evidence; the palette is a key.” Use original synthetic demo, make no claim to own Webb/Chandra photos, link to the free article. Grok social channels not touched.
