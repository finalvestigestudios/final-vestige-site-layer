# Media Recovery — Cosmos 954 / Operation Morning Light, WordPress post 279
**2026-11-10. Read-only source and archival investigation only. Draft PR #1703; NOT APPROVED FOR MERGE OR DEPLOY.**

## Verified scope
Authenticated WordPress `context=edit` read-back of published post **279**, “The Geologists Found the Spy Satellite” (modified 2026-11-02T21:39:54), yielded six literal `<img src>` URL values and six live ALT strings. All six URLs exactly match the frozen 2026-10-30 register. The frozen ledger does **not** preserve ALT text, so equality of present ALTs with historical ALTs has not been claimed. The article page and homepage were not changed.

Independent web-image retriever displayed exactly **279:0, :1, :2, :3 and :4**. It could not access **279:5 (LinkedIn tokenized image URL)**. These observations are *not HTTP GET statuses, CORS/CSP test results or logged-out browser outcomes*. Native direct HEAD to the Wikimedia host failed with local DNS resolution (no origin response). Actual guest status, natural pixel dimensions, wire bytes, redirects, referrer rules and caching remain **UNKNOWN**.

| Position | Visual and rights finding | Evidence / condition |
|---|---|---|
| **279:0** | Snowfield radiation search crew on commercial Polish CDN; photographer and permission unknown | Exact CDN image retriever-displayed. DOE/NNSA recovery photograph is a **different** candidate scene; no auto-substitution. |
| **279:1** | Red-white *Questor* survey Skyvan C-FQSL, illustrated by photograph from **Toronto, July 27, 1975**. It is **not** a photograph documenting the 1978 recovery mission. | Ontario's archived April 1976 survey report independently identifies Questor's C-FQSL geophysical aircraft, not its involvement in Cosmos 954. Exact Wikimedia photographer/license/native dimensions remain unverified. |
| **279:2** | Blue-background illustration with labels for Soviet nuclear reactor, sensors and transmitters; BCE/Baidu CDN lacks proven author/rights | Official DOE/NNSA artist's satellite scheme [Commons 354×229](https://commons.wikimedia.org/wiki/File:Cosmos-954_scheme.png) is different illustration, conditional candidate only. |
| **279:3** | **P1 inaccurate ALT:** exact four-panel collage shows snowy ground searches, a mission insignia and dispersed personnel. No aircraft appears, despite current ALT saying “aircraft”. | Editors should correct ALT after review, not silently swap the composite for an unrelated photo. Underlying four photographs/insignia/composite rights unknown. |
| **279:4** | LLNL-attributed BES-5 technical reactor scheme contains labels and explicitly marks some details **“assumed.”** | [Exact Commons catalog](https://commons.wikimedia.org/wiki/File:Cosmos-954_Reactor.png) lists original **640×958**, so conditional maximum is **640×958, never upscale to 960 width**. US-government licensing claimed, original LLNL employment/contractor authorship unconfirmed; label legibility is critical. |
| **279:5** | Tokenized LinkedIn-hosted photograph unavailable through independent retriever | **P0/P1 browser check**, not proven broken; source creator/rights and depicted scene all unverified. Government archive alternative is not confirmed the same photograph. |

### Proposed accessible copy (not published)
- **279:1:** “Questor International Surveys Skyvan photographed in Toronto in July 1975, illustrating the type used for geological surveys; not photographed during the 1978 recovery.”
- **279:3:** “Four-panel Operation Morning Light collage showing teams searching and handling instruments in snow, the mission insignia, and searchers across frozen terrain.”
- **279:4:** “Schematic of a BES-5 nuclear reactor showing labeled components, dimensions and coolant pipes marked as assumed.”

**Historical integrity:** No evidence yet that the 1975 Skyvan was the same aircraft used in Operation Morning Light, and the 2008-presented LLNL schematic is not an as-built Soviet original. Do not imply otherwise.

## Verified authoritative evidence
- [April 1976 Ontario survey report, page 2](https://prd-0420-geoontario-0000-blob-cge0eud7azhvfsf7.z01.azurefd.net/lrc-geology-documents/assessment/42F04NE0031/42F04NE0031.Pdf), identifies Short Skyvan C-FQSL operated by Questor (a geophysical survey **not** related to Cosmos 954).
- [DOE/NNSA Operation Morning Light photograph, Commons](https://commons.wikimedia.org/wiki/File:Cosmos_954_-_Recovery_002.jpg), item described as microwave transponder positioning; original 562×453. Rights claim must be verified to the originating federal source.
- [DOE/NNSA satellite scheme, Commons](https://commons.wikimedia.org/wiki/File:Cosmos-954_scheme.png), different artist's rendering, original 354×229. Do not substitute for published infographic without editorial review.
- [LLNL-attributed BES-5 schematic, Commons](https://commons.wikimedia.org/wiki/File:Cosmos-954_Reactor.png), original 640×958; labels and authorship/rights require verification.
- [Health Canada account](https://www.canada.ca/fr/sante-canada/services/securite-et-risque-pour-sante/radiation/urgences-radiologiques-nucleaires/incidents-accidents-anterieurs/cosmos-954.html), historical event context, not a photo reuse license.

## Machine-readable evidence and exact Git blob identifiers
- Six-image exact original URL/read-only ALT/retriever/candidate/rights audit: `qa/media-recovery/cosmos_279_six_live_primary_rights_20261110.json`, blob **`0a10945b4b98da17e688fb60cc4b69986b47d1ac`**.
- Whole 288-position reconciled ledger: `qa/media-recovery/coverage_263_exact_pr1703_20261110.json`, blob **`93f16b8731569352cbfde4a01a80d02709c342f2`**.
- Isolated fail-closed validator: `qa/media-recovery/validate_cosmos_279_six_20261110.cjs`, blob **`19d5b83fc52561fbc8c66784f2fe3d4ce279a8b3`**.
- 15-case regression suite: `qa/media-recovery/test_cosmos_279_six_20261110.cjs`, blob **`f41f21b35d6c3bf963b0df1fb8d9cbf0b8670740`**.
- **15/15 postcommit assertions passed** by running the committed test source with compatible V8 shims; native `node` CI and genuine guest Chromium still pending.
- Coverage now **263/288 (91.3%)**, **25 pending**, **268 evidence records**. Exactly six target rows changed, 282 unrelated rows unchanged.

## Site QA #154 handoff and no duplicate collector
Keep the original six P0 positions **285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1**. Then guest-check 279:5 in the existing collector. For each, capture `src`, runtime `currentSrc`, `srcset`, `naturalWidth/Height`, redirects and actual network response, `encodedDataLength` (or `null`), cache hit, errors/referrer/CSP, full-scroll and mobile visual appearance. Site QA owns the browser collector; this PR implements no redundant one. Do not label a web wrapper error as a browser 404.

## 76% image-weight claim, 42 broken claim, >1.5MB originals
The historic **42 reported broken** remain unconfirmed by guest browser. **76%** wire-byte savings remains unmeasured. Compare the *same* page/image identities with at least three cold-visitor runs per fixed mobile 390×844 and desktop 1365×768 viewport before and after approved staging changes. Transfer savings = `(baseline_actual_encoded_image_bytes - after_actual_encoded_image_bytes)/baseline_actual_encoded_image_bytes*100`. Do not derive savings from attachment stored size, resource timing opaque zero, downloaded-image pixels, redirects, cache hits or unrelated smaller substitutes. Guard LCP/CLS, mobile readability and visual matching.

Frozen oversize WordPress register still reports **15 originals >1,500,000 bytes, totaling 47,096,779 disk bytes**; **11 match expanded inline posts (38,480,915 disk bytes)**. Five published PNG originals (IDs 39–43, posts 34–38) have no generated WordPress subsizes; they are especially suitable for a **staging-only responsive-size investigation once permissions are cleared**. The 8.18MB media #388 has seven subsizes: do not assume visitors download its original. `docs/IMAGE-WEIGHT-WORKLIST.md` remained absent from main and draft branch; use the pinned `qa/media-recovery/cross_ledger_43_source_15_oversize_20261109.json` baseline instead.

## Publication and caching HOLD
Rights creator+primary item ID+license+commercial/derivative permission+required attribution, exact scene/date/crop, original pixels, and diagram label QA must all pass. For authorized sources only, conditionally create a `min(960,originalWidth)` version (and higher-resolution text-diagram exceptions only with approval); retain provenance, original and checksum; add WordPress media attachment and `width`/`height`/`srcset` **on an expressly authorized staging environment only**; verify guest decoding, captions, ALT, all links, LCP/CLS and rollback to prior URLs before separately approving live publication. **No media files downloaded, mirrored or cached; no license presumed; no WordPress write, risky Gutenberg block rewrite, homepage change, merge, deployment or spend.**
