# EX2 archival catalogue chain — follow-up to PR #1158

**2026-11-05 · Non-production editorial/engineering evidence · RELEASE HOLD.**
Base: draft PR #1158 exact SHA `82d3dd902a2a10c3c2ce4d8998`. Existing source image files, candidate layout, responsive `srcset`, WordPress media, and production content are **unchanged**. This report is neither a rights opinion nor a browser/network certificate.

## 1. Apollo 1 / WP 473 — identifier is findable; uploaded file still unverified

The previous review could not associate claimed identifier **S67-19766** with an independently indexed source record. A renewed *exact-number* search identified a catalogue entry labelled **NASA Identifier: S67-19766** in a DVIDS/NARA-labelled collection reproduced by a third-party archive index. Its title is **“ASTRO GRISSOM, CHAFFEE, WHITE IN VA, IN MISSION SIMULATOR AND ON COMPLEX 34.”** This significantly reduces the risk that the identifier was invented, but it does **not** prove that the uploaded, cropped/resized 1041×810 WebP is the same photograph.

References reviewed on 2026-11-05:
- [Secondary index: Apollo 1 holdings with item S67-19766](https://nara.getarchive.net/amp/topics/apollo%2B1)
- [Secondary index: item-specific S67-19766 listing](https://garystockbridge617.getarchive.net/media/astro-grissom-chaffee-white-in-va-in-mission-simulator-and-on-complex-34-4f44b4)
- [NASA's first-party Apollo 1 gallery](https://www.nasa.gov/gallery/apollo-1/) — gives history and other crew photographs; it does *not* independently associate the uploaded WebP with S67-19766.
- A published scholarly bibliography references `https://www.nasa.gov/sites/default/files/thumbnails/image/s67-19766.jpg`. That purported first-party image URL could not be retrieved/compared here, so treat it as a **reported, unverified link**.

**Why not close the image-identity gate?** The getarchive.net/PICRYL sites are third-party reproductions, *not* nasa.gov, archives.gov, or a verified DVIDS original record. Their item identity and generic subject corroborate an ID, but the local WP 473 image cannot be fingerprinted against a documented original from this tool environment. The reported large-image dimensions 7920×6160 have approximately the same aspect ratio as WP 473's 1041×810; that is **weak shape corroboration only**, not a visual/hash match.

**Release status:** Keep `source_identity=REVIEW_REQUIRED`, `uploaded_webp_binary_matched=false`, `primary_image_url_directly_verified=false`. Before release, obtain the actual first-party/original binary where permitted, record the source page and usage policy, do a controlled perceptual comparison (allowing resize/recompression), and log local SHA-256 plus exact browser-selected image HTTP receipt. Do not silently substitute the adjacent S67-19770 photograph; that is a distinct catalogue number.

## 2. Franklin Victory Point note / WP 474 — strong *size* corroboration, not byte proof

Wikimedia Commons' [specific file page](https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg) publicly lists:
- An original image **1576×2506 pixels**, **902,181 bytes**, SHA-1 `584cf387d7dcf3e259058ec14db2f4c7d04bac00`;
- A selectable Commons preview exactly **960×1526 pixels**;
- Public Domain Mark 1.0 and a file-history description indicating a scan from McClintock's **1869 printed edition**, rather than a newly licensed photo of the museum's physical artefact.

Connected WordPress media ID 474 declares **960×1526 pixels** at **466,043 bytes**. This is an exact dimension match to a listed Commons preview and supports the candidate's existing *1869 printed reproduction* wording. It does **not** prove that WP's JPEG is byte-equivalent to a particular Commons thumbnail or that no derivative changes were made. No local/upload or HTTPS-response bytes were downloaded.

**Release status:** Keep `wp_media_binary_matched=false`. Compare a fetched, documented Commons rendition to WP 474 by pixel/perceptual fingerprint and record its image-rights context. Continue distinguishing the Commons-marked reproduction from [Royal Museums Greenwich object HSR/C/9/1](https://www.rmg.co.uk/collections/objects/rmgc-object-504898) and any separately licensed museum photographs.

## 3. Negative boundaries and remaining mandatory gates

- NYPL WP 1258 remains **not embedded**. Nothing in this research grants rights to any NYPL digital capture.
- Neither metadata, dimensions, an index entry, an `<img src>`, nor a Javascript image-load check proves actual `currentSrc` response bytes or transfer cost. Existing PR #250 staging gate and PR #1114 exact-head evidence join remain authoritative.
- Only production WordPress site 256784396 is connected. A separate WordPress.com staging clone cannot be assumed on the Personal plan. Use the existing draft PR #1151/1136 isolated Playground path and **run** it; no claim that a real integrated import has passed.
- Genuine screenshot/keyboard/touch/no-JS/zoom/axe/Lighthouse measurement, independent QD/CI, founder approval, and anonymous Jetpack `/focus/` verification remain HOLD.
- Product and revenue acceptance remains offer → high-intent visitor → contextual CTA → verified lead → verified purchase → fees/refunds → net revenue. This review verifies **no** lead, purchase, or net revenue.

**Read-only coordination:** Homepage #150 / conversion #820, with Apollo #158 and Mind #171 kept independent; no Grok/Praxxis queue takeover. No subscriptions, affiliate claims, CMS writes, publishing, merging, deployment, analytics changes, or purchases.

**Decision:** Improved catalogue identity context for two archival sources, zero image-rights approvals, zero real HTTP image-body receipts. **RELEASE HOLD.**
