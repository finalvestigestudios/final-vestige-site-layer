# Flagship locked-folio local WordPress stage: exact-source audit (draft / HOLD)

## Verified blocking regression from PR #550 and PR #565

PR #550 **retired** the three-way visual direction selector after selecting Black Dossier × Museum After Hours. The standalone exact-source Chromium suites were corrected in companion PR #565 and a hosted workflow passed. **However,** `qa/release-candidate/verify_exact_staging.py` still demanded a visible `[data-fv-direction-choice="museum"]` on the *actual private WordPress preview*. That element no longer exists in `index.html`. This is a deterministic false failure of the WordPress acceptance gate, not a screenshot defect. It would prevent the first real staging attempt from producing an actionable acceptance report.

## Exact correction on this isolated child of PR #565

- Remove the obsolete direction-button assertion from `inspect_frame()`.
- Invoke `check_locked_editorial_identity(frame)` on the **actual rendered iframe** instead, checking seven invariants: no obsolete art picker or legacy attr; one visible, painted Franklin archival folio; dated 28 May 1847 original; April 1848 margin addition; editorial "NOT A FACSIMILE" notice; and the genuine RMG original-source link.
- Source-verify the imported gate on exact SHA inside `checkout()`, not just the main verifier.
- Add nine Chromium-backed tests, including eight adversarial distortions, using a representative **synthetic DOM** to verify the helper. This is **not** a WordPress render.
- Provide a draft-only GitHub Actions probe that fetches the official Assembler ZIP directly from the `Download` URL on WordPress.com's official theme page, constructs the **existing** private preview staging artifact, attempts actual loopback WordPress Playground and run of the existing five-width/axe/image HTTP acceptance suite. No public WordPress writes or data exports.

### Source / rights custody

Authenticated, read-only WordPress page ID 6 on November 1, 2026: published, modified October 30, 2026, all 72 unique Hidden in the Margins fragments (0–71), one Jetpack subscriptions block, two `/focus/` links. No modifications.

Source manifest `experience2/home-flagship/source-manifest.json` identifies Apollo image NASA S67-19766, Franklin Victory Point Note and 1903 NYPL BRT map. The Franklin folio is **editorial typesetting, not a facsimile**. Neither the 1903 map nor the astronaut image may be presented as literal evidence of the 1918 curve or hatch design. Original-image publication clearance remains outstanding for NASA context and especially NYPL item 5003296. WordPress media metadata gives 78,346, 466,043 and 5,553,669 bytes for originals, **not measured transfer bytes**. The workflow must obtain real HTTP payload evidence to clear that gate.

### Verification levels

**Completed in local Chromium:** 9/9 synthetic-rendered identity regression cases (one genuine success, eight adverse modifications rejected). No WordPress runtime used for this local test.

**GitHub-hosted WordPress/Assembler/axe/media:** `ex2-locked-folio-local-wordpress.yml` will provide source-and-environment evidence if it executes. Do not call this PASS until the exact run and screenshot/error receipts have been inspected. It intentionally uploads no browser storage state or user records.

**Theme provenance caveat:** The official WordPress.com HTTPS ZIP download proves the requested source URL and produces an observed SHA-256, but **the same-download checksum is not an independently approved out-of-band pin**. The CI receipt expressly overrides that release-gate flag to false and marks provenance HOLD. Reproducing official source origin is not a claim that the installed theme is identical to WordPress.com Atomic's current hosted build.

**Environment caveat:** Local WordPress Playground is not the WordPress.com Atomic host; it does not certify Jetpack signup, WordPress.com redirect/cookie/CSP parity, actual field p75 CWV, or the complete production page-6 preservation after any future migration. Do not attach authentication state to artifacts. The local page is private and not made the site front page.

## Release governance

No publishing, merging, production CMS/theme/navigation edits, staging deployment, upgrade, third-party subscriptions, or changes to frozen PR #49. No independent QD PASS, media-rights clearance, manual screen reader testing, real Safari testing, Lighthouse lab score or field CWV is claimed by these source changes. **RELEASE HOLD.**
