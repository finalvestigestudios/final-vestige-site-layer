# Apollo Experience 2.0 — R23 NASA catalog identity review, October 31, 2026

**Release posture: DRAFT/HOLD.** Isolated staged source only, stacked on R22 `e289e7e6f6633d7c83db8314e8c369004fea43db` (PR #319), independent of homepage PR #49, Research Desk PR #158, WordPress settings/content and live site. No NASA media is embedded. Atlas admission remains zero pins/edges.

## Primary sources and a specific unresolved identity

The PR #158 source ledger calls Research Desk record 01 `NASA S67-19766`. Apollo's canonical casefile record 01 instead uses `Apollo 1 crew training portrait`; both point to `https://www.nasa.gov/image-detail/apollo-1-crew-honored/`. NASA's linked page describes the Apollo 1 crew at Launch Complex 34 during January 1967 training but its page text does **not establish the catalog identifier**. The separate NASA page `https://www.nasa.gov/image-article/apollo-1-prime-crew-portrait/` expressly identifies a *different* crew portrait as `S66-30236` and dates that image March 31, 1966. Neither page alone certifies `S67-19766` as the accession for the linked casefile photo. **Do not substitute `S66-30236`, silently reconcile labels, or claim the first party confirmed the ID.** This is a read-only, manually reviewed snapshot, not a live NASA change monitor. The audit does not constitute NASA endorsement or image-reuse permission.

To resolve: obtain NASA first-party image metadata/caption explicitly binding the precise *linked photograph* to `S67-19766` or another verified number, then independently inspect photograph identity/caption date before proposing any amendment. Preserve each label and hold until adjudication. Source/rights evidence is distinct from geospatial pin admission.

## Implementation and custody

- Hash-pinned `qa/nasa_identity_witness_r23.json` with SHA-256 `75ef8e509b447bd61dcc3ae63400f49c260b80bf420de57082d34c41f5dac158` and fail-closed `verify_nasa_identity` on source mismatch, catalog-ID promotion, wrong date, photo substitution, rights or geolocation changes.
- Source-generated Research Desk crosswalk adds native HTML `<details>` Source Identity Review within the six-source comparison, with original NASA links, SourceDrawer/ChronologyRail anchors, 48px disclosure target, responsive 1–2-column source comparison, no-JS complete semantics, no third-party embeds.
- Deterministic private Apollo PHP staging builds hash-seal expanded HTML/CSS. Read-only admission now rejects missing/renamed `hold` label, missing source links, or swapped image-equivalence witness.
- `qa/test_nasa_identity_r23.py`, R23 staging-admission adversarial tests and `qa/browser_catalog_identity_r23.py` add reproducible regression coverage.

## Locally executed QA (NOT real WordPress or production CWV)

- Python/PHP unit and simulated HTTP privilege/nonce/admission checks: **143/143 passed**.
- Real Chromium/Playwright R23 component: **7/7 widths 320,360,390,768,1024,1440,1920 passed**, keyboard/touch/no-JS/reduced-motion, 420px embedded-column overflow, source links and native disclosure.
- Existing Chromium primary suite, AX tree, crosswalk, Wayfinder, Atlas, Rights, Custody Receipts and Dual Witness: **each 7/7 passed** (after updating a strict selector for nested native `<details>`).
- No actionable elements without accessible names in the Chromium AX-tree local test. `php -l` passed. Two byte-identical private package builds, see R23 artifact checksum manifest.
- Synthetic LCP/CLS are in included JSON; no claims about real field Core Web Vitals. Strict axe-core gate deliberately fails closed without a verified version-pinned axe-core bundle.

## Non-waivable release blockers

No actual installed WordPress/Assembler/Jetpack staging; HTTP browser-origin navigation/CSP and cookies not certified; verified axe-core unavailable; no Safari/VoiceOver/NVDA or hosted p75 LCP/CLS/INP; NASA six-photo individual media reuse rights pending; unresolved record 01 ID; no green CI on exact head, independent QA, founder-selected art direction or founder deployment authorization. **Do not merge/install/deploy.**

Reproduce under `experience2/apollo-wp-bridge/sealed/` with Python, PHP and Python Playwright with Chromium:

```
python -m unittest discover -s qa -p 'test_*.py' -q
python qa/browser_catalog_identity_r23.py
python qa/browser_exact.py
python qa/ax_tree_r16.py
python qa/browser_wayfinder_r22.py
python qa/browser_crosswalk_r18.py
python qa/browser_atlas_admission_r19.py
python qa/browser_media_rights_r20.py
python qa/browser_custody_receipts_r21.py
python qa/browser_dual_witness_r17.py
php -l fv-ex2-apollo-sealed-template.php
python qa/browser_exact.py --require-axe  # expected nonzero (missing verified axe)
python build_sealed.py --out /tmp/r23-private-a.zip
python build_sealed.py --out /tmp/r23-private-b.zip
sha256sum /tmp/r23-private-{a,b}.zip  # must match
```
