# Apollo Experience 2.0 R19 — curated Atlas admission / withheld geography

**2026-10-31 | DRAFT/HOLD — SOURCE REVIEW ONLY, NOT PUBLICATION**

Parent: Apollo R18 draft PR #294, exact commit `cbcf3e576decbe7df624551d68761fe51996f075`. Canonical original Apollo casefile source head `74375657f2cdaac0710f94c6de6c24534ee06858`; Research Desk PR #158 read-only witness head `250d7f05a4de037e73826dcf0cfaef0ec4c29383`, blob `403d128c57b9bc82dac7c619651689070edef86c`. The homepage PR #49, lead homepage branches, original PR #158 and canonical Apollo PR #215 are outside this workstream.

## Actual implementation

- Added `qa/atlas_admission.py` as a **build-time gate** over the original six published-investigation cards in source-pinned `generated/fragment.html` (WP listing IDs **434/621/370/269/37/433**). Requiring exact WP ID/title/theme/HTTPS published URL, six source entries, original no-map status, no new executable/media/geographic attributes prevents silent changes to atlas custody.
- Injected an accessible native `<details>` **inside** the existing Atlas, with six readable admission cards and links to original investigations. Links, IDs, titles and themes derive solely from the original pinned source; these are **source-listed published URLs, not live availability verification**. No image bytes, coordinates, point geometry, geocoded regions, link edges, or unsourced relationships were introduced. Search/filter on original Atlas remains intact and fail-open without JavaScript.
- Added authenticated, nonce-guarded `atlas-admission.json` source-custody export: six original source-listings, **zero approved coordinates, zero edges, six pending primary-location reviews**. JSON explicitly says that no media rights or WordPress availability has been cleared.
- Staging-only PHP response now requires the exact admission asset before HTML is emitted, includes SHA-256 provenance headers for the admission HTML and export, and serves the latter exclusively over the existing editor/nonce-protected download endpoint. No new public file route.
- Read-only staging HTTP admission verifies the exact extra asset headers and export bytes; adversarial tests require fail-closed behavior on header corruption, export mutation, changed WP IDs, changed source URL, tampered category, altered geolocation status, invented data latitude and injected SVG.
- No uploads or production changes. Original WP content, plugin settings and all NASA images are untouched. The item-level NASA photo reuse review and the PR #158 catalog-label discrepancy (`NASA S67-19766` versus Apollo descriptive title) remain unresolved HOLD conditions.

## Reproducibility and evidence

From `experience2/apollo-wp-bridge/sealed/`, with Python 3, PHP and Python Playwright + `/usr/bin/chromium` installed:

```bash
python -m unittest discover -s qa -p 'test_*.py' -q
python qa/browser_exact.py
python qa/browser_atlas_admission_r19.py
python qa/browser_dual_witness_r17.py
python qa/browser_crosswalk_r18.py
python qa/ax_tree_r16.py
python build_sealed.py --out /tmp/R19-private-review.zip
python qa/browser_exact.py --require-axe # MUST fail closed if no verified bundle + SHA-256
```

**Actually executed locally**: **102/102** Python/PHP unit, custody, security, HTTP-stub and adversarial checks PASS; exact-source Chromium/Playwright **7/7** widths (320, 360, 390, 768, 1024, 1440, 1920px) PASS; independent R19 Atlas-disclosure browser **7/7** PASS; original R17 dual-witness **7/7**, R18 crosswalk **7/7**, and Chromium CDP accessibility-tree **7/7** PASS. R19 checks actual `<details>` keyboard Enter, screen-reader named links in browser AX tree (six new named links), 390px no-JS disclosure and source list, 420px WordPress-like nested layout, reduced motion, zero root overflow. Five existing and two new staging asset integrity headers are checked through real local PHP HTTP responses under a **synthetic WordPress shim** (not installed WordPress). Screenshots captured at 390 and 1440px with SHA-256 entries in `qa/R19_ATLAS_BROWSER_RESULTS.json`.

Two independent ZIP builds are byte-for-byte identical, **SHA-256 `9e822777dc61f593fabdb3adf9388d87d9a62dc7d7cce567b74503be6c283604`**, embedded PHP **SHA-256 `54b913a6d88bc07f04d2d31dd805460b40686d3353cf08f7eae9c7707ca5e5c5`**. The package has 13 SHA-256-protected assets, no public static media files. Local synthetic LCP is **232–588ms** in 6/7 viewports, **unavailable at 1440px**; synthetic CLS **0** at all 7 viewports. These are not hosted or field Core Web Vitals; p75 LCP, INP, CLS have not been validated. CI status must be checked for exact published commit separately.

## Non-waivable blockers

- Real verified axe-core bundle is unavailable here; `--require-axe` **exits nonzero** as designed. CDP AX coverage does not mean WCAG 2.2 AA compliance.
- No installed separate WordPress staging environment with actual Assembler theme / Jetpack / block shortcode; local HTTP tests use a synthetic PHP shim.
- Chromium browser-enforced remote/loopback HTTP CSP, frame, cookies and auth are not verified in this tool environment; synthetic meta CSP is only a browser smoke approximation.
- No manual NVDA/VoiceOver, Safari/iOS, real-device or hosted p75 CWV/INP, green exact-head GitHub CI, independent QD, individual NASA media clearance, or founder art-direction signoff.
- **Research Desk photo label mismatch** remains an explicit editorial hold. Matching original NASA page URLs is not independent validation of NASA photograph catalog identifiers.

**Decision:** DRAFT / HOLD. Do not merge, deploy, install the ZIP, write WordPress content/settings, or touch homepage PR #49. NASA original media remain linked, not copied.

Background official sources: https://www.nasa.gov/gallery/apollo-1/ ; https://www.nasa.gov/image-article/apollo-1-crew-honored/ ; https://www.nasa.gov/nasa-brand-center/images-and-media/ .
