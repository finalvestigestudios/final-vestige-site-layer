# Media recovery: November 15 live 132-image WordPress census and featured/inline split

## Evidence, scope and exact counts

This is a **read-only** image-performance and visual-integrity review on existing draft PR #183, separate from homepage design and Site QA PR #154. Two authenticated, paginated WordPress media-list reads (100 + 32 image attachments), one published-post list, and four published-post edit-content reads were completed on 2026-11-15 Pacific. Full source URL/bytes/dimensions/parent-ID metadata are frozen in [132-row JSON](../qa/media-recovery/wp_132_media_66_posts_20_oversize_20261115.json).

- **132 image attachments**, **90,403,013 original stored bytes**; **66 currently published posts** (WordPress posts-list results). This is **not** a new census of inline image tags.
- **20** originals are strictly larger than **1,500,000 decimal bytes**, totaling **64,385,752 stored original bytes**, or 71.22% of the stored originals. The previously reported **16 / 49,107,665 B** is reconciled *exactly* by four newly uploaded oversized featured assets totaling **15,278,087 B**.
- The frozen earlier audit of **61 posts / 355 stored inline image references** is a historical cohort, not the fresh 66-post WordPress list. The **42 reported broken third-party images remain unconfirmed by a genuine guest browser**; the supposed **76% wire-weight reduction remains unmeasured**.
- **No production image repair** or actual guest-browser origin status/response bytes was performed by this audit. Stored-original bytes cannot be used as a saving estimate.

## Four new oversized assets: actual published attachment role

The following four media attachments are assigned as `featured_media` to their respective published articles. **The exact first-party attachment URLs do not occur in those articles' stored inline `<img>` tags**, which still reference separate external Commons image URLs. Theme/card/hero display may use the featured attachment or a Jetpack variant; neither its actual `currentSrc` nor downloaded transfer bytes are known.

| Post | WP media ID | Stored original | Native dimensions | Proportional <=960px review | Archive/rights |
|---|---:|---:|---:|---:|---|
| [Piri Reis](https://finalvestige.com/2026/11/02/piri-reis-map/) #1917 | 2640 | 7,422,309 B | 1964 x 2619 | **960 x 1280** | [Exact Commons source](https://commons.wikimedia.org/wiki/File:Piri_reis_world_map_01.jpg); PD-Art tag; map labels/zoom needs human review |
| [Mesmerism](https://finalvestige.com/2026/11/02/mesmerism/) #1924 | 2636 | 4,462,854 B | 2988 x 3538 | **960 x 1137** | [Commons CC BY 4.0](https://commons.wikimedia.org/wiki/File:%22Le_Baquet_de_Mesmer%22_Wellcome_M0006352.jpg), **source rights conflict**, see below |
| [Lycurgus Cup](https://finalvestige.com/2026/11/02/lycurgus-cup/) #1920 | 2638 | 1,745,282 B | 2720 x 3649 | **960 x 1288** | [Photographer Chappsnet, CC BY 4.0](https://commons.wikimedia.org/wiki/File:Front_of_4th_century_CE_Roman_Lycurgus_Cup,_British_Museum_(1958,1202.1).jpg) |
| [Crystal skull](https://finalvestige.com/2026/11/02/crystal-skulls/) #1926 | 2637 | 1,647,642 B | 1436 x 2001 | **960 x 1338** | [Photographer Vassil, CC0 1.0](https://commons.wikimedia.org/wiki/File:Crystal_Skull_British_Museum_26072013_05.jpg) |

**Rights warning for M0006352:** The Commons file attributes its image to Wellcome, advertising CC BY 4.0, but the current [Wellcome archival catalogue record M0006352](https://wellcomecollection.org/works/q75g4rar) labels the related June 1939 negative **“In copyright.”** Catalogues may describe different legal layers or records. Do **not** infer that this is definitely infringement or that either source overrides the other. Obtain an authoritative provenance/permission decision and reconcile the exact binary before any new rehost, replacement, derivative or credit rewrite.

The Commons photo-file dimensions and byte counts are consistent with these WordPress media metadata, but **not cryptographic proof that the WP binaries are identical to those Commons files**. This sprint downloaded no image binaries, so source SHA-256 and actual origin responses remain unknown. Likewise the British Museum name in an image title does **not** automatically license the photographer's creative photograph.

## How this changes optimization priority

**P0:** Site QA #154's existing cold, logged-out, full-scroll visitor collector must first establish which of the six already selected broken-image candidates actually fail (post/image keys `285:5`, `285:2`, `287:5`, `418:1`, `418:2`, `407:1`). Do not duplicate its collector, report web-retriever errors as real HTTP statuses, or silently replace historical scenes.

**P1:** These new featured assets should be measured separately from inline originals. Reconcile actual theme/Jetpack `currentSrc` and CDP transferred bytes at 390x844 and 1440x900, with cache/memory/service-worker negatives and request-ID proof. Featured-image savings must not be added to inline-image savings without unique-request de-duplication.

**P2 (staging plan, no writes authorized):** After per-file rights/binary identity review, use an isolated staging copy, choose derivatives no wider than `min(960,native_width)` with proportional heights, retain map detail/zoom, protect attribution and the original historical scene, compare rendered mobile/desktop visual results (including captions/ALT/CLS), capture before/after *transferred* image bytes with the existing CDP protocol, and prepare a reversible media-ID/featured-template rollback. If the 7.4 MB Piri Reis map needs readable detail, do not silently replace it with an illegible static 960px-only image.

## Offline QA and integrity checks

`node --check qa/media-recovery/validate_wp_media_census_20261115.cjs`

`node --test qa/media-recovery/test_wp_media_census_20261115.cjs`

`node qa/media-recovery/validate_wp_media_census_20261115.cjs qa/media-recovery/wp_132_media_66_posts_20_oversize_20261115.json`

The two committed JavaScript files exactly match a locally executed native Node suite: **15/15 pass**, including adversarial forged visitor HTTP status, invented 76% savings, false inline claim, illegal publish approval, duplicated ID, threshold conflation, 960px geometry, missing rights and unverified binary/redirect claims. GitHub readback separately recomputed 132/66/20 and 90,403,013 / 64,385,752 / 15,278,087. Repository CI and guest Chromium remain unrun.

**Boundaries:** zero WordPress production writes, no external binary copying/caching, no Gutenberg block rewrites, no homepage/design changes, no duplicate Site QA collector, no PR merge/deploy, no paid subscriptions.
