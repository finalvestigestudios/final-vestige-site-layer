# Apollo R80 — date-precision-preserving NASA photograph chronology

**STAGING_HOLD / draft only.** Tracks [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150). Stacked on source-only R79 [PR #705](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/705) at `604f4b5f01745125eff0a5f8ede6623f02c326ef`. No change to Research Desk PR #158, frozen homepage PR #49, homepage engineering branches, NASA source audit, NASA image media files, or WordPress production.

## Specific historical interpretation defect

R79 rendered an ordered photographic chronology `03 → 02 → 01 → 05 → 04 → 06`. Source **01** is explicitly only dated **January 1967**, without a verified day. Positioning its entry after January 3 and before January 28 could be read visually as a narrower date claim, even though explanatory prose disclaimed it. The two January 24, 2017 retrospective exhibit photographs also appeared as separate sequential items despite sharing the same photograph date.

## R80 correction

- The ordered `<ol>` contains **four known calendar-day checkpoints**, in date order: 1966-10-18 (source 03), 1967-01-03 (source 02), 1967-01-28 (source 05), and 2017-01-24 (sources 04 and 06 in **one same-day group**). HTML `<time datetime>` preserves machine-readable day precision.
- The January 1967 portrait (source 01, proposed `S67-19766`) is now **outside the ordered list** in a distinct, headed uncertainty note with `<time datetime="1967-01">`. Its day is unresolved, and it cannot be ordered before or after either known January photograph.
- Every source retains its NASA URL, content limitation, 6 source cards, complete source disclosure and printable custody; **zero NASA images**, scripts, invented coordinates, relationships, or rights approvals are introduced.
- Responsive, native keyboard/touch/no-JS, reduced-motion, forced-colors and local screenshot/PDF behavior remain required. The date rule is asserted in both Python source-contract tests and every real Chromium JS/no-JS configuration at 320–1920px, not just editorial copy.
- Updated inline CSS groups same-date links visually with 48px target height, without remote fonts or assets. No WordPress application component is changed; this is a **static staging gallery**, not actual hosted WP.com compatibility.

## Reproduce / exact-head CI

```sh
python -m unittest discover -s experience2/evidence-atlas/tests -p test_nasa_gallery_r79.py -v
python -m unittest discover -s experience2/evidence-atlas/tests -p test_nasa_chronology_r80.py -v
python experience2/evidence-atlas/tests/build_nasa_gallery_r79.py --repo . --head "$(git rev-parse HEAD)" --out /tmp/R80_NASA_GALLERY.zip
python experience2/evidence-atlas/tests/browser_nasa_gallery_r79.py --repo . --out /tmp/R80_BROWSER --axe /path/to/pinned-axe.min.js --require-navigation --require-axe
```

The independent `.github/workflows/ex2-apollo-r79-nasa-pages.yml` runs these tests and the existing R79 browser suite, screenshot checks, same-run axe, print and lab LCP/CLS. A workflow definition **is not a CI pass**. Verify exact commit and artifacts before making an acceptance claim. Original R79 audit JSON is immutable in this sprint.

## Separate inherited QA warning

The R79 head's R79-specific workflow passed, but its **separate inherited WordPress/Assembler workflow** failed in the R77 synced-pattern browser extension after the original 14 ordinary WordPress cases had each reached PASSED. The downloaded artifact `R69_FAIL_CLOSED_RECEIPT.json` identifies `wordpress_r68.py:390`, where `accept_synced_patterns` begins. Its precise internal assertion was not included in the sanitised receipt; this is **not** demonstrated to be an R79-gallery defect, and **not** a genuine WordPress regression pass. Inspect and resolve exact-head failure before declaring broad CI green.

## Release blockers

This staging gallery does not clear photograph-by-photograph media rights (all six PENDING), `S67-19766` catalog identity, hosted WordPress.com acceptance, independent editorial/QD review, physical-device and NVDA/VoiceOver evaluation, field CWV, or founder release approval. No merge, deployment, CMS content/settings write, speculative geography or unreviewed paid service is authorized.
