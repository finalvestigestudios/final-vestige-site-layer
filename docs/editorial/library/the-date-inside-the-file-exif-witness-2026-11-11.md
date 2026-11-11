# The Date Inside the File — EXIF Witness Desk

**Final Vestige Studios Library · November 11, 2026 · RELEASE CANDIDATE / PUBLIC HOLD**

## Reader problem and distinction
A JPEG metadata timestamp may date a camera exposure, a later scan or a software export. It is not an independent certificate of the age of a depicted historical event. This resource complements the published *The Missing Caption* (visual and catalog identification) by examining embedded technical EXIF fields and file integrity, with a locally run, privacy-first JPEG inspector.

## Completed artifact and rights
Original illustrated, self-contained HTML article + interactive JPEG APP1 Exif inspector, original SVG scene/object/file diagram, 7-step methodology, local SHA-256 in secure browser contexts, hidden-until-revealed GPS, and local witness JSON export that **never includes precise GPS**. Printable four-page PDF field cards with eight linked sources. Original synthetic JPEG fixtures, source and rights register, reproducible scripts, and SHA-256 manifest supplied in conversation ZIP. No third-party scans, photographs, institutional seals or standard figures reproduced, and no external analytics/CDN/upload code.

## Official sources — checked 2026-11-11
1. CIPA / JEITA [Exif Version 3.1 (DC-008-Translation-2026)](https://cipa.jp/e/std/std-sec.html), issued January 30, 2026. Institutional text checked; specification linked, not reproduced.
2. Library of Congress [Exif 2.2 digital-format description](https://wwws.loc.gov/preservation/digital/formats/fdd/fdd000146.shtml), previous Exif format (NOT the 2026 version). Direct institution text checked.
3. LOC [Daguerreotype cataloging conventions](https://www.loc.gov/pictures/collection/dag/cataloging.html). Institution indexed; direct ordinary-browser verification **OPEN** (reader 403).
4. NIST [Digital Evidence Preservation, IR 8387](https://www.nist.gov/publications/digital-evidence-preservation-considerations-evidence-handlers), 2022; official record updated 2026-11-05. Direct page checked.
5. NARA [Copyright and Permissions, Still Pictures](https://www.archives.gov/research/still-pictures/permissions). Direct institution text checked; item-level rights not presumed.
6. LOC [Keeping Personal Digital Photographs](https://www.digitalpreservation.gov/personalarchiving/photos.html). Institution indexed; direct browser verification **OPEN** (reader timeout).
7. NARA [Digital Photographic Records, 2003](https://www.archives.gov/records-mgmt/initiatives/digital-photo-records.html). Direct page checked; **SUPERSEDED** and used solely as history, not current transfer policy.
8. NIST [Digital Investigation Techniques, IR 8354](https://www.nist.gov/publications/digital-investigation-techniques-nist-scientific-foundation-review). Direct institutional page checked.

All external institutional pages are linked only. Rights, licenses and availability of specific photographs require independent item-level verification.

## Local QA
- 320, 390, 768, 1440 pixel standalone Chromium rendering, JavaScript enabled and disabled: **8/8 responsive checks PASS**, no page-wide horizontal overflow or uncaught JS exceptions. Screenshots inspected at 390 and 1440.
- Synthetic EXIF fixture date and device decode, GPS concealed/revealed/rehidden, invalid URL scheme rejection, inert HTML-like input, JSON export, precise-GPS omission, form and file resets, missing EXIF and non-JPEG rejection: **20/20 local checks PASS** (includes viewport cases).
- Four-page PDF rendered and visually inspected; links embedded. ZIP integrity test PASS.
- **Honest test limitation:** Chromium in this environment blocked all external and localhost/file navigations; browser tests used `set_content` in an insecure about:blank context, so native `crypto.subtle.digest` was not available. Code degrades with an explicit message. HTTPS-native SHA-256 functional test remains OPEN. Browser-local EXIF decode and privacy behavior were actually tested.

## Release blockers — no live WordPress write
1. Actual production-theme 320/390/768/1440 screenshots with inspectable pixels, keyboard controls, accessibility and anonymous download checks (shared blocker [#1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589)).
2. HTTPS-native SHA-256 and page integration test.
3. Ordinary-browser confirmation for two reader-limited LOC URLs, plus all outward links.
4. Per-first-publication WordPress/Jetpack email and social suppression, including `_jetpack_dont_email_post_to_subs=true` where supported.
5. Hosted PDF/media, draft WordPress metadata, minimal Library card, canonical and anonymous visitor readback.

Do not publish a duplicate source directory. Existing [#1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788) 90-source correction remains the higher publication priority. No public WP changes, subscriber sends, social publishing or spending.

## Artifact digests
- HTML SHA-256: `cfdb789dc3c81048f020c20f08356e0406874588dfdb7b75f62f8f5ef97dbd96`
- PDF SHA-256: `c0251aaabc1a15a984a69cb25dd4170a2f0ec0f302aa8b195f2fe1167b4c6014`
- Rights CSV SHA-256: `6752f0ec78a621593e87474716fb0a4d450a43018ceaf8f6fab5019fe4e83cdc`
- QA JSON SHA-256: `83b29d38b563c387abc1d6261a818190f0dc9f2cbf4c1c9e4690abd61dc682d8`

Editorial standards: https://finalvestige.com/editorial-standards/ · Related published resource: https://finalvestige.com/the-missing-caption/
