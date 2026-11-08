# FV Experience 2.0 — archival media custody admission (2026-11-08)

**Decision: RELEASE HOLD.** This is an actual read-only source/rights assessment of the existing protected seven-chapter review package, not native WordPress, a network transfer test, or legal permission to use archival images in commercial advertisements. It does not modify PR #49, the protected preview ZIP, or WordPress production.

## Inspected source

- Protected private Playground bundle from PR #1626 inherited through PR #1645. Archive SHA-256: `23c4073fb328ae6231380f68225af36645ab127b8df864e604aee1848f54b436`.
- Actual protected PHP components rendered using non-WordPress PHP stubs, as in PR #1633. This output **is not WordPress Core**.
- Authenticated WordPress media API records 473 (NASA), 474 (Franklin), 1258 (NYPL), read November 8, 2026. Site 256784396.
- Primary source/rights records linked below. WordPress upload-file byte counts **are not proof that a browser received those bytes**.

## Actual preview and source-rights assessment

| Item | WordPress attachment metadata | Preview | Rights scope / outstanding |
|---|---|---|---|
| Apollo 1 / NASA S67-19766 | #473, WebP 78,346 bytes, 1041×810 | **Rendered** | NASA reuse of released imagery is generally allowed under media conditions; NASA credit, no endorsement, identifiable-person and third-party restrictions remain. Do not put this astronaut image into an unreviewed product endorsement or advertisement. Confirm exact origin and transferred bytes. |
| Franklin Victory Point Note | #474, JPEG 466,043 bytes, 960×1526 | **Rendered** | Wikimedia Commons identifies the file as public domain, from the 1869 McClintock *Voyage of the Fox* printed reproduction. This is **not** a museum-issued photograph of the original physical note. Confirm bytes match the displayed file. |
| 1903 NYPL Brooklyn Rapid Transit map | #1258, JPEG 5,553,669 bytes, 5667×3831 | **Source link only; not a preview image** | NYPL believes the precise map is public domain **in the U.S.**, with no determination for other countries. Preserve NYPL credit/source link. The WP derivative's identity and actual transferred image bytes remain unverified. |

Primary source links:

- NASA brand/media guidelines: https://www.nasa.gov/nasa-brand-center/ and https://gpm.nasa.gov/image-use-policy
- Franklin public-domain file: https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg ; museum's original object record: https://www.rmg.co.uk/collections/objects/rmgc-object-504898
- Exact NYPL item and territorial rights limitation: https://old-digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0

## Executable admission

Run the source-controlled tool against privately rendered HTML from the protected candidate; don't publish that fixture:

```bash
python3 experience2/review/verify_archival_media.py \
  --ledger experience2/review/archival_media_custody.json \
  --html /path/to/private/review.html --self-test \
  --report /path/to/private/media_report.json
```

**Result actually obtained against the protected candidate:** **9/9 controls pass**, image source/alt/dimension/srcset and source-link inventory passes for both rendered images (2/2); all three attachment records are in the ledger. Network-byte transfer returns **BLOCKED: NETWORK_BYTES_NOT_SUPPLIED**, intentionally exits 2, and final verdict is HOLD. Tested negatives include added or swapped image, changed alt or dimension, absent primary citation, unreviewed srcset origin, absent transfer, and forged transfer receipt.

The verifier accepts an optional PRIVATE transfer directory and independently obtained JSON receipt keyed by asset: `source_url`, HTTP `http_status=200`, `received_bytes`, and actual `sha256`. It checks uploaded original filesize, image header, and decoded dimensions. A self-supplied receipt alone cannot establish remote provenance: retain and independently review browser network/HAR evidence, without exposing cookies or subscriber data.

## Release gates and ownership

**Built / tested:** static source inventory and conditional editorial rights audit, 9/9 isolated controls. **Not tested:** actual WordPress Core and Assembler, browser image transfer, Jetpack, independent axe/WCAG 2.2 AA, Lighthouse, hosted CWV, product orders, affiliate transactions. The container cannot resolve/download WordPress Core or pinned Assembler and has no isolated WP environment; WordPress.com Personal does not provide a native staging clone. No subscription upsell is justified.

**Offer → Funnel → Blocker → Change → Evidence → Owner:** The existing free 52-page Focus Fieldbook remains the lead-capture offer; reliable archival media and source credibility are trust prerequisites for evidence readers. Blocker: provenance and image-byte delivery were repeatedly represented by WP metadata only. Change: source-controlled rights and byte-transfer admission. Evidence: authenticated metadata + primary catalogs + 9 passing static/negative controls, while actual transfer correctly blocks. Interim homepage engineering owns this review; Claude retains Jetpack/analytics engineering, Grok/Praxxis retain creator distribution, and founder controls production release/spending. No new links, tracking, content, plugin installs, sales or subscribers.

**Next release test:** execute existing protected Blueprint in an authorized free isolated WordPress Playground with pinned Assembler; capture exact real image bytes, secure network evidence, 320–1920px real browser screenshots and interaction/no-JS/zoom/reduced-motion checks; run exact-head #250/#252 CSP, axe, Lighthouse, independent QD/CI and preserve Page 6 + native Jetpack before considering founder approval. No merge/deploy/publish authorized.
