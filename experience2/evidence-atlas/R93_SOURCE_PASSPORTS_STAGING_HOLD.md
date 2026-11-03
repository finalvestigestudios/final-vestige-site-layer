# Apollo Experience 2.0 / R93 Source Passport Shelf — STAGING HOLD

**Owner:** Apollo Evidence Studio, independent of homepage PR #49 and its lead engineering lane.  
**Upstream:** R92 draft PR #783 (not PR #158); all four prior Apollo review surfaces remain intact.  
**Issue:** #150. **Publication:** explicitly prohibited until separate founder release approval.

## Deliverable

R93 adds a fifth, accessible, text-only **Source Passport Shelf** for the six NASA references. Unlike the chronology and Research Reading Room, it offers a compact per-source reference card, what-the-photo-can/cannot-establish boundary, a native SourceDrawer disclosure, native links to all four established presentations of the **same record**, a downloadable reference-text document, and a machine-readable JSON bibliography. Optional JavaScript offers a keyboard-operable "Copy reference" action with a polite status message and a safe failure fallback; all citations, source links, facts and disclosures remain usable without JavaScript. Copying a reference conveys **no media rights**.

## Provenance and build constraints

The R93 builder accepts **only a fresh R92 generated staging directory**, not manually entered Apollo claims. It validates R92's source-binding and rights-gate receipt and all its per-file SHA-256 digests, parses the six **actual R88 EvidencePlates**, cross-checks record titles, dates, catalog claims, and limitations against the actual R89 Hub records, and verifies each NASA href against the inherited six-record custody register. The R92 builder itself inherits the original R91 / R90 / R86 Research Desk and generated Evidence Atlas verification. Provenance failures halt export.

R93 **does not** embed NASA media, assert rights clearance, create geographic pins, infer historical edges, invent dates, or imply the January 27, 1967 fire can be reconstructed from photo dates. Source 01's proposed S67-19766 association and month-only photograph date remain provisional; sources 04/06 share the January 24, 2017 photograph date without a claimed order. All six individual photo-use reviews remain **PENDING**.

Example read-only exact-head build from repository root (Python 3.12):

```bash
python experience2/evidence-atlas/tools/build_reciprocal_routes_r92.py /tmp/apollo-r92
python experience2/evidence-atlas/tools/build_source_passports_r93.py --src /tmp/apollo-r92 --out /tmp/apollo-r93 --archive /tmp/apollo-r93.zip
python -m unittest discover -s experience2/evidence-atlas/tests -p test_source_passports_r93.py -v
```

Generate a second archive from a second empty target and compare byte-for-byte. The ZIP has fixed timestamps and lexically ordered entries. Its contents include the original four inherited view surfaces, R93 passport HTML/CSS/JS, reference TXT/JSON, and a machine-readable SHA-256 receipt. The public-facing preview is explicitly indexed `noindex,nofollow`; this remains staging-only, not published.

## Real Chromium acceptance

The R93 isolated CI workflow pins Playwright, browser, axe-core, and PyMuPDF. It tests widths **320, 390, 768, 1440 and 1920px**, with JavaScript enabled and disabled; verified per-source NASA destinations, source boundaries, zero unauthorized photographs/maps, zero unexpected network requests, horizontal overflow, Enter/Space native disclosure, mobile touch and same-page fragment links, optional reference-copy feedback, reduced-motion context, forced-colors focus, **actual axe** WCAG scans at 390/1440, observed LCP and CLS, reproducible viewport screenshots, and Chromium-native PDF text extraction proving six NASA URLs and mandatory rights warnings.

These tests produce **laboratory** measurements, not field p75 CWV. Automated axe results do **not** establish manual NVDA/VoiceOver, actual device, hosted WordPress.com or independent QD acceptance.

## Release blockers

- All **six** photo-specific NASA image reuse assessments and possible third-party rights constraints require independent review; source linking is not image-use clearance.
- NASA catalog association `S67-19766` is provisional pending NASA confirmation.
- Authorised hosted WordPress.com isolated-install compatibility, manual screen readers, physical-device/browser matrix, independent QA, and production p75 CWV data remain open.
- The intermittently failing Gutenberg synced-pattern LCP laboratory gate is unresolved.
- No publication, homepage branch edits, PR #49 edits, PR #158 edits, WordPress content/settings writes, or paid services. Explicit founder visual/release approval and governed release review are required before any deployment.

**Status:** staging candidate; no merge, installation or production authorization.
