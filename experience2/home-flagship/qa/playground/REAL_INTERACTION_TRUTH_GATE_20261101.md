# Complete-home WordPress HTTP replay: real interaction truth gate
**2026-11-01 · DRAFT / RELEASE HOLD · homepage engineering only**

## Exact source and intentionally narrow scope

Parent: PR #500 at exact SHA `626ebb7e2a76ff679a20f9adc7573559bb06d259`; its prior HTTP replay source has Git blob `8afbd3d62695263ac90329e4d201332cafc804bb`. The protected v1 PR #49, homepage Gutenberg source, seven chapters, Franklin folio, WordPress page 6, Apollo and Mind lanes were not edited.

PR #252's offline exact-head CSP suite correctly verifies four interactions *on a canonical in-memory source fixture*, while PR #490's separate **actual-local-HTTP WordPress render replay** verified resources, seven widths and no-JS evidence **but not actions**. A rendered source with all controls visually inert could pass PR #490. These are distinct lanes; this change closes that gap without duplicating #252's CSP or claiming native WordPress.

## Real fail-closed actions now required on *each* width (320/360/390/768/1024/1440/1920)

1. Direction controls: Museum changes `data-fv-direction`; Dossier restores it.
2. Evidence case: Franklin selection hides Apollo; keyboard ArrowRight selects Malbone; Home restores Apollo. Selection must change **actual visibility**, not just ARIA.
3. Chronicle: the addition layer changes mode, and original mode restores it.
4. Observer: selecting B makes B visible and A hidden; selecting A restores the inverse.

All four are included in the resulting per-width receipt under `real_interactions`; a missing control, inert handler, failed restore, or failed keyboard transition fails the replay. The previously existing seven-width layout/image/source/resource checks remain.

With JavaScript disabled, verify all three cases and both Observer frames remain visible *and* all four enhancement control groups are hidden. A no-JS page may explain the evidence rather than pretending controls work.

## Red/green evidence — honest browser test boundary

- **Before:** locally executed exact PR #490 replay bytes (`8afbd3d...`) against a controlled Python HTTP test server with three 1px synthetic GIF exhibits and deliberately inert JS: **false PASS**.
- **After:** corrected replay source (`c80d97c...`) on those exact controlled inputs: **FAIL**, all four interaction requirements unfulfilled. Inert/ARIA-only/keyboard-missing variants are likewise rejected.
- **Valid fixture:** baseline and corrected Chromium 144 replay PASS; the corrected runner observes all four real reversible interactions, keyboard navigation and no-JS evidence. Synthetic screenshots were pixel-identical (390x900) on both baseline and corrected valid inputs. Screenshots of synthetic fixtures are **NOT** archival imagery, native WP or founder preview.
- Nine new Chromium adversarial unit tests passed. Seven existing HTTP capture regressions passed unchanged. Twelve existing resource-completeness tests passed with Chrome viewport reduced to 390 for speed, while the new positive path explicitly exercised all **seven** widths. This is **28 unique passing local tests in split runs**, not an assertion of a full unmodified, exact Git checkout suite. Each source file's Git blob identity has been checked independently.

Reproduction from an exact checkout with installed Python packages (Playwright, beautifulsoup4), browser executable, and permissions for local synthetic HTTP:

```bash
cd experience2/home-flagship/qa/playground
python -m unittest test_replay_wordpress_stage_browser -v
python -m unittest test_replay_resource_completeness -v
python -m unittest test_replay_real_interactions -v
```

For real WordPress replay, see `WORDPRESS_HTTP_REPLAY_FALLBACK_20261101.md`. This runner still accepts only approved local resources, an **independently reviewed** three-image SHA manifest and complete seven-chapter rendered WordPress HTML.

## Explicit remaining nonrelease gates

No real WordPress/Assembler instance was launched here; no authenticated NASA/Commons/NYPL image bytes, archival source rights clearance, exact private WordPress screenshot, axe WCAG 2.2 AA, Safari, host CSP/cookies/Jetpack, Lighthouse, p75 field CWV, hosted GitHub CI/QD or founder visual/release approval. HTTP-to-DOM replay is useful lower-bound visual evidence but **cannot certify** those conditions. WordPress.com Personal provides no native clone; free isolated WordPress Playground/local staging is still the correct route, without a subscription upgrade. **DO NOT install, merge, deploy, publish or edit production.**
