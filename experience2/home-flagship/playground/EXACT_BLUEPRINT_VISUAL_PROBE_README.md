# Exact-Blueprint source visual probe — draft / NO RELEASE

**2026-11-06.** This is a local Chromium witness for the *exact embedded HTML/CSS/JS of the integrated Playground Blueprint*, created to replace synthetic mockups with source-derived evidence while the private WordPress/Assembler instance is not available to this runner. **It is NOT itself WordPress, not an Assembler render, not a private staging site, not production, and not a release certificate.** No production writes or new paid tools.

## Source and reproducible run

Baseline: [PR #1237](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1237), SHA `5ec27b48b0ace971f48c779fa3ba26d213452374`. Download the authenticated exact Blueprint to local disk, never point public Playground at a private repo branch. Run:

```sh
python -m unittest experience2/home-flagship/playground/test_exact_blueprint_visual_probe.py
python experience2/home-flagship/playground/exact_blueprint_visual_probe.py experience2/home-flagship/playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json --output .local-ex2-source-review
# Optional native axe-core JS path: --axe-core /path/to/axe.min.js
# Optional downloaded Blueprint checksum pin: --expected-sha256 <actual_sha256>
```

Requires Python Playwright + local Chromium. It uses `page.set_content` to avoid blocked file/localhost navigation in restricted Chromium execution; this also **does not emulate the WordPress URL, origin, cookies, scripts enqueue order, CSP, or CDN**. The probe emits a local noindex HTML source witness, 12 first-screen screenshots across six widths, extracted source byte counts, seven-chapter and 72-Margins DOM inventories, real `img.currentSrc`/decode indicators, broken image requests, Focus links/visibility/touch-height, reduced-motion visibility, overflow and (only when supplied) real axe results. Mark failed images honestly; **do not count requests blocked by this isolated browser as live CDN failures**.

## Status and explicit blockers

**BUILT:** New extractor and viewport probe; source is read from the existing 5-step Blueprint, not a lookalike or generic fixture. **TESTED:** Local implementation was run against a clearly labeled synthetic fixture (12 Chromium cases); source-delimiter admission was independently checked on the actual 142,374-character Blueprint from GitHub. **NOT TESTED:** actual 7-chapter image decode/network, exact Blueprint Chromium/screenshots, WordPress/Assembler integration, keyboard/touch/manual screen-reader review, 200% native zoom, CSP, real axe if unavailable, Lighthouse and field CWV. **NOT LIVE.** A successful synthetic run does not qualify the site.

Next: import this existing Blueprint inside isolated **WordPress Playground + pinned Assembler**, capture its real browser-served output at 320/360/390/768/1440/1920 and check source/file hashes, archive network bytes, reduced-motion all 72 records, keyboard/touch/no-JS, axe and Lighthouse. Then validate anonymous live Focus/Jetpack separately with founder-specific release approval. The WordPress.com Personal plan cannot create native staging; **do not recommend an upgrade by default**. PR #49 remains frozen. PR #158 Apollo R&D and issue #171 Mind editorial are separate lanes. No affiliate links, extra scripts or revenue assertions were added.

**Offer / funnel / blocker / experiment:** Existing free 52-page Focus Fieldbook → homepage secondary CTA → published CTA points at investigations; draft PR #1201 proposes Focus link → this probe measures source-grounded mobile visibility/touch height without publishing → Site QA assesses, Claude owns attributable lead/order reporting → verified paid revenue remains unknown.
