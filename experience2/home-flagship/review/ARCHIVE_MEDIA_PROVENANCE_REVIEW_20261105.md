# Final Vestige Experience 2.0 — archive-media source, rights & delivery decision
**Read-only review: 2026-11-05.** Based on the canonical seven-chapter candidate at draft PR #1151 parent `56b6663af5e3933377a495a7e326468a9c83819b`. This review is **not** a license, legal opinion, media delivery test, WordPress render, CI/QD pass, or permission to publish.

## What was actually inspected

1. Source-controlled `experience2/home-flagship/index.html` (Git blob `8f4d64186c986a00ac48e23db7df2c05a610ceaa`) and the pinned WordPress Playground Blueprint (Git blob `a415e9ca446b340de1f345b693a7269a0e5d6037`). Exactly **two** `<img>` tags appear in the canonical candidate: Apollo 1 and Franklin. Malbone uses editorial chronology **without** reproducing the NYPL map.
2. WordPress.com production **read-only** media records: IDs 473, 474, 1258. Their `media_details.filesize` fields are **metadata**, not measured network transfers. No production write occurred.
3. Official source/custodian records: NASA Apollo 1 image article, Royal Museums Greenwich object HSR/C/9/1, Wikimedia Commons Franklin file and stated PD mark, NYPL's rail-map research guide and rights guidance. All linked below. No image bytes were fetched into this review environment because external requests are unavailable in the execution container.
4. This source candidate includes Jetpack's `https://i0.wp.com/` domain in both responsive `srcset` attributes, despite first-party base `src` URLs. The browser can select that CDN. A `finalvestige.com` `src` attribute **does not establish first-party actual delivery**.

## Exhibit 01 — NASA Apollo 1 image, WP media 473

- **Actual source in candidate:** `https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp`.
- **Recorded file:** image/webp, 1041×810 px, 78,346 bytes (WP metadata). Alt text identifies Gus Grissom, Ed White and Roger Chaffee near LC-34 in January 1967. Caption attributes NASA image **S67-19766** and avoids NASA endorsement.
- **Independent corroboration:** NASA itself describes the three astronauts posing near Launch Complex 34 in its [2022 Apollo 1 remembrance](https://www.nasa.gov/image-article/remembering-apollo-1-astronauts/), and hosts an [Apollo 1 gallery](https://www.nasa.gov/gallery/apollo-1/). A readily retrievable official 1967 crew-at-pad photo is also labeled **S67-19770** in other indexed sources. **We did NOT verify that S67-19766 is the matching NASA original**; similarity of the subject or NASA's general public-domain posture is not image-specific proof.
- **Rights handling:** Government-created NASA photographs generally have a US public-domain basis, but institutional trademarks/endorsement and third-party contributor exceptions matter. Do not call this precise transformed WebP definitively verified until its original NASA record and transformation chain are reconciled. No NASA partnership or endorsement wording.
- **Decision:** `REVIEW_REQUIRED` for identifier/source chain. The existing image stays in unpublished study; no production media change.

## Exhibit 02 — Victory Point note, WP media 474

- **Actual source:** `https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg`.
- **Recorded file:** image/jpeg, 960×1526 px, 466,043 bytes (WP metadata); alt explains 1847 text and handwritten 1848 addition.
- **Independent corroboration:** [Wikimedia Commons: Franklinexpeditionnote.jpg](https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg) marks the historical image public domain; the site's existing attribution identifies it as a scan from an 1869 printed reproduction. The physical object is held by [Royal Museums Greenwich, HSR/C/9/1](https://www.rmg.co.uk/collections/objects/rmgc-object-504898), whose record confirms the May 28, 1847 message and the April 26, 1848 addition.
- **Important distinction:** The *museum's photographed collection image* is not automatically covered by Commons file rights. RMG separately advertises image licensing. The candidate explicitly says the displayed scan is a Commons-marked public-domain reproduction, **not** the museum-supplied photograph. Keep that qualifier. The locally transformed 960px JPEG is not yet byte/visual-proven to match the Commons derivative.
- **Decision:** Historical subject/source and Commons marking are supported; local file lineage and real browser response remain release checks. Do not describe editorial typesetting as a facsimile.

## Referenced but not embedded — NYPL map, WP media 1258

- **Recorded file:** image/jpeg, 5667×3831 px, 5,553,669 bytes (WP metadata), claimed NYPL image ID **5003296**. The [NYPL transit guide](https://libguides.nypl.org/nyc-rail-transit/companies) cites image 5003296 in its 1903-map section.
- **Rights:** NYPL [rights rules](https://api.repo.nypl.org/api_documentation_v1) distinguish `No Known U.S. Copyright`, `CC0`, copyright held/managed and undetermined **at the capture level**. A general collection statement or WordPress caption is insufficient to validate this specific upload and its transformations.
- **Decision:** Do not embed the original or its responsive variants in the flagship candidate until the precise NYPL capture record and jurisdictional use basis are recorded. Continue with the original editorial chronology, source link and uncertainty note. It is **not** included in the proposed Playground bundle.

## Required acceptance for an authorized isolated developer rendering

1. Render the actual exact-source WordPress/Assembler candidate at 320, 360, 390, 768, 1440 and 1920 px, plus browser 200% zoom. No-JS must retain both historical exhibits and source context.
2. Record for each image the browser-selected `currentSrc` host, response HTTP status, decoded response-body byte count, SHA-256, final redirect URL, intrinsic size and visible screenshot. Check Jetpack `i0.wp.com` redirects and privacy/CSP implications. **Do not equate 78,346/466,043 declared bytes with response bytes.** Source URLs and WP dimensions alone are not receipts. Existing PR #1114 contains the release evidence-integrity join; attach real producer receipts rather than inventing another standard.
3. Reconcile the precise NASA source identifier, verify Commons-to-local Franklin derivative provenance, and keep NYPL excluded absent capture-specific rights. Record source-page URLs, capture dates, allowed use and caveats. Publication gate fails if source identity or rights remain unsupported.
4. Keep production homepage Page 6, its 72 Hidden in the Margins entries and Jetpack Focus signup intact. Check the guest-facing `/focus/` form separately; Playground cannot prove Jetpack signup or conversions. Measure actual Lighthouse/axe performance only in a real browser and label environment differences. No new affiliate benefit claims or tracking.
5. Existing isolated Playground Blueprint has **not** been executed here; current WordPress.com Personal plan has no native staging clone. No plan upgrade is proposed. Frozen PR #49, Apollo PR #158 and Mind issue #171 remain untouched.

## Conversion relevance and decision

**OFFER:** existing free 52-page Focus Fieldbook. **FUNNEL:** source-backed historical exhibit → trust/CTA clarity → `/focus/` guest signup → independently confirmed lead → verified paid purchase. **BLOCKER:** unresolved source-image custody and unmeasured third-party responsive image delivery weaken trust/performance evidence before users encounter the CTA. **CHANGE:** exact media/rights ledger plus negative-control source-custody gate. **EVIDENCE:** source-linked metadata comparison; no network or real browser tests completed. **OWNER:** homepage engineering for image/UX integration; independent editorial/QD for rights; Claude for attribution and commerce; Grok/Praxxis for acquisition. **RESULT:** no confirmed subscribers, paid orders or net revenue established.

**Current state: BUILT/REVIEWED, NOT RELEASE-QUALIFIED. Decision: HOLD.** This dossier closes source provenance *inventory* ambiguity, not source licensing or image-transfer acceptance. No production CMS writes, merging, deployment, affiliate activation, posts, analytics changes or spending.
