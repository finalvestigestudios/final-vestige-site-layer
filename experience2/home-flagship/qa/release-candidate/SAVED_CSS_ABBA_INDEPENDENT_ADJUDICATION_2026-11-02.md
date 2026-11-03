# Exact-Gutenberg ABBA CSS-order — independent evidence adjudication

**2026-11-02 Pacific | DRAFT / RELEASE HOLD.** Source PR #713 exact SHA 7cd762501880d86e955a138e3ec60d48d5dda549. No WordPress writes or deployment.

## Verified provenance

Original GitHub Actions run 41563937676: successful isolated WordPress/Assembler job.
Artifact ID 13198428528, ex2-ephemeral-assembler-wordpress-HOLD, complete ZIP SHA-256:
b9520d3c4742d9cc56fa332993619a2b24d1c0f1a04500ef2ba94abcf5b57a29 (independently calculated and matches GitHub digest).

Source receipt: GUTENBERG_SAVED_CSS_ORDER_ABBA.json in this exact ZIP.
All four genuine 390x844 Chromium first-screen screenshots have identical PNG bytes, each SHA-256:
44e515b501ad742a2f31a346e0ce335927cb824f79dd52d774440e417f04c5dc.

## Same-run 390px cold-cache 4xCPU / 150ms RTT / 1.6Mbps comparison

| Variant | Four LCP samples (ms) | Median (ms) |
| --- | --- | ---: |
| Early CSS (ABBA positions 1 and 4) | 3172, 3180, 3180, 3148 | **3176** |
| Late CSS (ABBA positions 2 and 3) | 4128, 4276, 4064, 4100 | **4114** |

Observed lower early CSS median LCP: **938ms / 22.8%**. This is within-run observational evidence, not a randomized causal experiment. Both variants have exactly seven chapters, native Gutenberg save/readback, identical mobile visual captures and browser HTTP 200. All four early LCP trials still **FAIL** the 2.5-second lab target.

Other observed tradeoffs: median FCP early 2476ms vs late 2534ms; maximum CLS early 0.05095 vs late 0.00235; median desktop LCP early 1196ms vs late 1124ms. Desktop is 72ms slower early. These are *lab-only* and not production field Core Web Vitals.

## Reproducible independent data gate

Source-controlled assess_css_abba.py requires the full original GitHub ZIP, its expected digest and exact source SHA. It validates image identities, ordered A/B/B/A samples, per-variant Gutenberg source consistency, browser profiles, metrics and provenance, and prints HOLD regardless of performance. Fourteen synthetic adversarial tests passed locally. New exact-head source-only CI workflow must also pass before counting GitHub tests as verified.

From the repository root (ZIP sourced from that GitHub Actions artifact, never committed to source):
~~~
python experience2/home-flagship/qa/release-candidate/assess_css_abba.py --artifact /private/FV_PR713_ABBA_QA.zip --sha256 b9520d3c4742d9cc56fa332993619a2b24d1c0f1a04500ef2ba94abcf5b57a29 --head 7cd762501880d86e955a138e3ec60d48d5dda549
python -m unittest discover -s experience2/home-flagship/qa/release-candidate -p test_assess_css_abba.py -v
~~~

## Release position: HOLD

This narrows the CSS order performance diagnosis but does **not** clear mobile 2.5s, hosted WordPress.com compatibility, manual WCAG/device acceptance, rights, independent QD or founder release approval. Published WordPress homepage ID 6 (modified 2026-11-02 17:48:13, revision 1914 per prior readback) currently includes an NYPL Malbone map *image* absent from rights-safe source candidate. Image-specific rights permission is unverified; this is a custody/approval discrepancy, not a legal allegation. Do not overwrite/rollback live content without separately authorized release steps. Preserve Focus Fieldbook, native Jetpack signup and all 72 Margins. Frozen PR #49 and Apollo/Mind lanes untouched. This PR creates no public CMS writes, image fetches, affiliate claims or new paid dependencies.
