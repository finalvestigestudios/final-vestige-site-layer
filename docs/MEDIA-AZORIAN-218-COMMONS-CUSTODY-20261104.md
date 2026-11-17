# Media Recovery: Project AZORIAN post 218 — Commons redirect custody and right-sized geometry (2026-11-04)

**Scope:** Isolated PR #183 only. Read-only WordPress and archival metadata; not Site QA's browser crawler, homepage visual design, production or a media download.

Read-only live WP post 218 is **published** (modified **2026-10-29 16:01:32**) with exactly **six <img> source URLs and ALT strings** matching frozen `parts/06.json` SHA `0f3dfe398a76838049cebba7cb773d5c5a0c8c69`. **0/6** have inline HTML width/height attributes, so CLS risk exists but is not measured.

All six use **Commons Special:Redirect/file URLs with `?width=1280`**. Independent text retrieval could not resolve any of the six exact redirect URLs: **not** origin 404/403 or a logged-out browser failure. Commons file catalog records for each name remain accessible. No binary was fetched or compared, and a matching filename is not a proven matching crop/binary.

## Catalog identities, original dimensions and non-upscaled maximum
| Slot | Identity | Catalog master | Conditional maximum |
| --- | --- | ---: | ---: |
| 218:0 | CIA 2022 manganese nodule | 800×533 | **800×533** |
| 218:1 | USNS Glomar Explorer U.S.-government-credited ship photograph | 1280×833 | **960×625** |
| 218:2 | CIA 2022 Summa patch | 800×533 | **800×533** |
| 218:3 | 2022 CIA Museum photograph of K-129 model | 3598×2400 | **960×640** |
| 218:4 | 2022 Sherman Wetmore at AZORIAN painting | 800×709 | **800×709** |
| 218:5 | 2022 CIA Museum coveralls and ashtray | 2400×3598 | **960×1439** |

The two 2022 museum photograph *catalog masters* are reported as **5.47 MB and 4.93 MB** respectively; the published `?width=1280` request may use a smaller responsive rendition. Never equate those catalog master bytes to actual visitor transferred bytes or claim 76% savings. Three catalog files already max out at 800 px, so no 960px enlargement. Conditional heights are rounded from catalog geometry, **not** decoded production image sizes.

## Primary source and rights checks
CIA's [Project AZORIAN exhibit](https://www.cia.gov/legacy/museum/exhibit/project-azorian/), [manganese nodule](https://www.cia.gov/legacy/museum/artifact/manganese-nodule-encased-in-lucite/) and [2022 Sherman Wetmore report](https://www.cia.gov/stories/story/honoring-the-mission-of-project-azorian/) support subject identities. The two museum images trace to [CIA's 2022 museum press account](https://www.cia.gov/stories/story/modernized-cia-museum/) and CIA Flickr entries as noted in their individual Commons catalogs. Commons labels these PD-USGov/PD-CIA; **per-item creation, license provenance, credit and use restrictions remain HOLD** pending review. The ship photo's exact federal photographer/agency and original negative remain insufficiently identified; do not treat the general description as a rights release.

## Conditional staging
1. Site QA #154 finishes its existing P0 queue first (285:5/2, 287:5, 418:1/2, 407:1). For post 218, logged-out cold browser capture should record all six `currentSrc`, redirects, actual Image GET HTTP/MIME, `naturalWidth`, decode(), screenshots, CLS and CDP encoded bytes. Record whether Commons returns a smaller image when 1280 was requested.
2. If a broken image is **browser-confirmed**, match archival identity and exact visual crop; document item rights, attribution and source URL; only then prepare a 960px-or-smaller derivative with a stable filename and image hash. Preserve captions and actual historical subject. WordPress staging requires a separate explicit approval.
3. Compare versioned cold CDP bytes against the *same six displayed historical scenes* (desktop and mobile separately), not catalog masters; reject percentage claims without the fixed 61-post/355-slot cross-site method and complete before/after evidence.
4. Keep rollback record of original `src`, ALT and caption. No blanket hotlink replacement, inferred copyright, publishing, homepage edits or subscription cost.

[Six-row JSON audit](../qa/media-recovery/azorian_218_six_commons_20261104.json) · [strict validator](../qa/media-recovery/validate_azorian_218_20261104.cjs) · [adversarial tests](../qa/media-recovery/test_azorian_218_20261104.cjs). The text retriever's inability to resolve redirect endpoints is **not** a production-failure count. Sitewide baseline **61/355/288/13**, 42 reported failures still unverified in visitor browsers; 76% transfer reduction unmeasured; zero production repairs.
