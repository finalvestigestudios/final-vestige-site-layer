# EX2 — Archival rights and original-file transfer gate (2026-11-10)

**DRAFT · READ-ONLY · NO PRODUCTION/WORDPRESS WRITES · release HOLD.** Parent PR #1920 exact SHA d91cc8bdfba2870dc02196ce75a558ccac3c4e44; frozen PR #49 unchanged. Coordinated with Issues #150 and #820, Apollo PR #158 and sealed preview PR #224. The public WordPress Page 6 remains the published homepage, not the candidate.

## Evidence/rights ledger, based on fresh WP media 473/474/1258

| Image / WP original | Reported bytes | Primary rights evidence and limitation |
| --- | ---: | --- |
| Apollo crew, NASA image S67-19766, media **473**, original s67-19766.webp | **78,346** | WP credit includes NASA and no-endorsement disclaimer. NASA's [Brand Center](https://www.nasa.gov/nasa-brand-center/) generally permits agency historical/editorial imagery but prohibits implied product endorsement and cautions about identifiable people's publicity rights in advertising. **Conditional**: match the exact uploaded transcoded original against the NASA catalog/source and inspect any third-party notices. Do not use astronauts' likenesses to endorse affiliate products. |
| Franklin Victory Point note, media **474**, Franklinexpeditionnote.jpg | **466,043** | WP correctly says **scan of an 1869 printed reproduction**, not a photograph of the 1847/1848 original. [Wikimedia Commons file page](https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg) identifies McClintock's 1869 source and applies public-domain marking. **Conditional**: compare uploaded derivative with sourced scan; keep facsimile/editorial typesetting descriptions and source citation. |
| NYPL BRT 1903 map image 5003296, media **1258**, edit-017-v02-nypl-5003296-original.jpg | **5,553,669** | [NYPL research guide](https://libguides.nypl.org/nyc-rail-transit/companies) identifies the 1903 source and image ID. [Exact NYPL item record](https://old-digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0) explicitly marks believed public-domain **in the U.S. only**, status in other countries undetermined; it requests voluntary credit and source link. **Conditional**: the site's edited v02 version must be matched to the original; do not extrapolate global clearance. |

These are defensible documentary leads, **not legal clearance**, proof of exact uploaded file identity, commercial endorsement rights, or proof of network transfer. Existing alt/captions were checked read-only; no new images, historic claims, or affiliate promises introduced.

## Executable original-byte gate

New tools/experience-2/verify_ex2_media_bytes.py uses no third-party dependencies. **Default is offline** and marks each file NOT_TESTED; it never pretends that WordPress attachment metadata equals an HTTP transfer. With **explicit** --network, it GETs only the three hard-coded public first-party original URLs, requiring HTTPS/final host and path, HTTP 200, correct MIME, actual reported original byte count, image signature (WebP or JPEG) and SHA-256 output. Failures exit nonzero. It never uses WordPress credentials, changes CMS, inspects visitor data or uploads anything.

Commands from repository root:

    python -m unittest discover -s tests -p 'test_ex2_media_bytes.py' -v
    python tools/experience-2/verify_ex2_media_bytes.py
    python tools/experience-2/verify_ex2_media_bytes.py --network --out actual-firstparty-media-result.json

Local source-equivalent tests: **12/12 PASS**, including synthetic positive fixtures and negative controls for wrong host, CDN, URL query, external redirect, HTML injection, invalid MIME, wrong sizes, corrupt JPEG. Source-equivalent fixtures were NOT the real images. GitHub CI/QD exact-head remains outstanding.

**Critical gap:** the engineering runtime cannot resolve public hostnames; no real first-party media byte transfer was completed. Photon/Jetpack i0.wp.com responsive transformations can use different sizes and MIME; the checker intentionally covers **only original first-party files**, not browser srcset, responsive images, delayed loading, image LCP, network waterfall, or full WordPress rendering. Those require genuine isolated WordPress/Assembler staging and Chromium network capture. WordPress.com Personal has no native staging clone; don't request a paid upgrade without cost/benefit approval.

## Conversion-first release decision

**Offer:** original free 52-page Focus Fieldbook. **Funnel:** qualified social/historical entry → credible sourced media → clear Focus CTA → genuinely confirmed subscriber → independently verified purchase/net revenue. **Blocker:** unverifiable media transfer/rights undermines trust, rendering and load performance. **Change:** exact-site documentary rights review + explicit reproducible media-byte gate. **Evidence:** NASA, Commons, NYPL source statements + live WP metadata + 12 local simulated tests. **Status:** built/tested locally, **NOT network verified or live**. **Owner:** interim engineering/media gate; Claude owns integration/attribution; editorial/rights reviewer owns source-identity signoff; founder alone approves production release. No newly verified paid conversions or revenue.

**Release HOLD** pending actual WordPress/Assembler acceptance, full responsive image transfers/rights, WCAG 2.2 AA including keyboard/touch/no-JS/zoom, real Lighthouse/CWV, Jetpack confirmation, independent CI/QD exact SHA, founder preview and explicit approval. No production publishing/merge/analytics/affiliate actions.
