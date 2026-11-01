# Apollo R33 — NASA source-identity custody annex (STAGING HOLD)

R33 is an isolated, source-controlled editorial addition to Experience 2.0 Apollo 1, stacked on the R32 Apollo QA branch. **Do not merge, install, activate or deploy.** Homepage PR #49, homepage engineering branches, Research Desk PR #158 and WordPress remain untouched.

## Editorial correction and purpose

PR #158's original Research Desk labels its first record `S67-19766` while linking NASA's Apollo 1 Crew Honored catalog page. That NASA page describes a January 1967 Apollo crew photograph but **does not verify that catalog identifier**. R33 retains an explicit HOLD rather than using a third-party source to manufacture equivalence.

A NASA photograph cannot by itself establish every claim the associated Apollo Review Board text makes. R33 distinguishes October 1966 chamber training, January 3 1967 spacecraft preparation, January 28 1967 post-fire damage and January 24 2017 retrospective museum displays. All six are individually source-linked, captioned with limits and left **link-only pending media rights review**. There are no admitted geographic pins or relations.

## Files

- `nasa_catalog_primary_r33.json`: six fixed NASA catalog URLs, context dates, original-credit strings, evidentiary limits, rights and catalog-identity holds, checked 2026-10-31.
- `nasa_catalog_custody_r33.py`: fail-closed registry, original sealed PHP source HTML crosswalk and zero-geo admission; emits HTML-escaped, offline no-JavaScript annex and exact SHA-256 receipt.
- `nasa_catalog_annex_r33.css`: responsive charcoal/gold reading cards, 44px native disclosure controls, strong keyboard focus, reduced-motion and print presentation.
- `test_nasa_catalog_custody_r33.py`: adversarial source/rights/date/geo tests. Missing PHP fixture is clearly marked **SKIP**, never silently counted PASS.
- `browser_nasa_annex_r33.py`: real Chromium no-JS responsive 320,360,390,768,1024,1440,1920 checks, keyboard and pointer disclosure activation, zero outbound requests/images/scripts, 390/1440 reproducible screenshots.

## Run locally, without WordPress writes

The R32 helper `browser_csp_projection_r32.authorized_php_response()` can render exact R29 sealed PHP over loopback with explicitly mocked WordPress functions; save its response body to a **private** file. Do not commit nonce-bearing PHP HTML.

From this QA directory, with Python, BeautifulSoup4, PHP, Playwright, and Chromium installed:

```bash
export FV_APOLLO_CASEFILE_HTML=/private/path/to/exact-r29-php-response.html
python -m unittest -v test_nasa_catalog_custody_r33.py
python nasa_catalog_custody_r33.py --registry nasa_catalog_primary_r33.json \
  --casefile "$FV_APOLLO_CASEFILE_HTML" --out /tmp/apollo-r33-annex.html \
  --receipt /tmp/apollo-r33-source.json
python browser_nasa_annex_r33.py --registry nasa_catalog_primary_r33.json \
  --shots /tmp/apollo-r33-shots --receipt /tmp/apollo-r33-browser.json
```

## Source registry

1. https://www.nasa.gov/image-detail/apollo-1-crew-honored/ — January 1967 portrait, `S67-19766` alias NOT verified on page.
2. https://www.nasa.gov/image-detail/amf-s67-15717/ — January 3 1967 preparation.
3. https://www.nasa.gov/image-detail/amf-s66-58038/ — October 18 1966 chamber rehearsal.
4. https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/ — January 24 2017 tribute.
5. https://www.nasa.gov/image-detail/amf-s67-21294/ — January 28 1967 post-fire evidence.
6. https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/ — January 24 2017 hatch tribute.

NASA policy: https://www.nasa.gov/nasa-brand-center/ . NASA non-endorsement, third-party rights and publicity considerations are NOT cleared simply by linking.

## Actual local R33 evidence, 2026-10-31

- **16/16 Python cases PASS** with actual PHP-generated sealed casefile loaded; source crosswalk finds six NASA catalog records and six image rights holds.
- **7/7 real Chromium 144 widths PASS**, with JavaScript disabled; keyboard Enter and pointer activate the native `details` elements, no overflow/embedded images/scripts or outgoing requests.
- Original source holds maintained: six NASA catalog records, six media-use holds, one disputed catalog alias, zero approved geo pins or edges.
- Adversarial test found a previous root-level `#atlas[data-lat]` oversight; the validator was corrected and mutation tests now reject this case.

**Boundaries:** This is NOT installed WordPress staging. Chromium direct HTTP navigation is blocked by sandbox policy. No verified axe-core, Safari/VoiceOver/NVDA, browser-enforced HTTP-header CSP, hosted Lighthouse/p75 CWV, historical image rights approval, independent QD, or green hosted CI. Screenshots are local synthetic staging evidence; no claims of production compliance.
