# R66 — Complete Apollo NASA source-custody matrix / STAGING_HOLD

**Scope:** Issue #150, stacked on R65 (#616), not on PR #158, homepage PR #49, or any homepage branch. Changes are isolated to `experience2/evidence-atlas/`. Neither an installed WordPress environment nor production is changed.

## Reproduced defect

R65 guarded NASA image URLs, photographic dates, individual reuse status, and a few selected custody strings, but did **not** protect the full SourceDrawer record. In actual Chromium, replacing a displayed NASA credit with an unsupported commercial-reuse assertion and triggering a search left the Atlas enhanced (`data-fva-ready="yes"`); that assertion could flow into the downloadable evidence sheet. The original reviewed crosswalk and NASA-page audit had not changed. This is editorial integrity drift, not a demonstrated attacker exploit.

## Correction

The Atlas runtime now pins **all 54 displayed `dt`/`dd` field values** against the exact R37 custody crosswalk and SHA-256-pinned R55 NASA-page metadata ledger. The table includes identity notes, NASA catalog verification limits, displayed credits, producing centers, NASA page-update dates, research-check date, reuse disclaimers, and documentary boundaries. A mismatch suppresses optional filters/comparison/download and restores the six source cards. Native disclosures, six citations, and print records remain readable. There is no network fetch, photograph embedding, invented geographic pin, asserted rights clearance, or modification to the original Research Desk. This is a source-drift guard, not a hostile-script security boundary.

## Execution / reproducibility

- `python -m unittest discover -s experience2/evidence-atlas/tests -p 'test_*.py' -q`
- `python experience2/evidence-atlas/tests/browser_r66_custody_matrix.py --output qa-r66`
- `python experience2/evidence-atlas/tests/browser_r65_all_targets.py --output qa-r66/regression-r65`
- `python experience2/evidence-atlas/tests/build_full_staging_r66.py --output staging-r66`
- `python experience2/evidence-atlas/tests/build_r66_bundle.py --qa qa-r66 --output Apollo-R66-STAGING_HOLD.zip`

R66 browser suite: 32 viewport/JS/forced-colors/reduced-motion cases, 54 individual field-mutation cases, three pre-initialization mutations; original R38 and built Atlas are executed through the PHP WordPress API simulator. It is **not genuine WordPress**. The R65 all-native-control browser suite is a separate regression. Both maintain zero external requests and check print completeness, no-JS behavior, 200% reflow, and deterministic screenshots. Local LCP and CLS are **fragment laboratory observations**, not hosted p75 metrics.

## Holds / production prohibitions

Do not publish or merge without approved actual WordPress/Assembler staging, independently checksum-verified axe-core, NVDA/VoiceOver, hosted CWV, independent QD, and successful exact-head CI. Six NASA photographic reuse reviews remain pending, including recognizable people/third-party rights, and S67-19766 catalog association remains provisional. NASA general media guidelines do not alone clear an individual photograph or allow implied NASA endorsement. No changes to WordPress content, settings, production, PR #49, or Research Desk PR #158.
