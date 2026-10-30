# Experience 2.0 — Sprint 03: Research Desk & integration candidate

**Status:** Functional research software, locally verified; NOT installed, merged, approved, or deployed. Separate from pending homepage PR #49.

## Actual deliverables

- Third standalone, source-driven prototype: **Research Desk / Source Ledger** for the Apollo 1 investigation, based on the published Final Vestige article (WordPress post 434), Apollo 204 Review Board report, and six original NASA image source records.
- Six semantic evidence cards, each exposing the record's ID and source URL, the editorial finding, and a required explicit evidentiary limitation. Native HTML `details` elements provide context without JavaScript.
- Optional JavaScript search + live count. The filter shows/hides only static cards, does not inject HTML, call APIs, store tracking data or require third-party libraries. If JS is absent, all six records and their archive links remain accessible.
- `source-ledger/build_ledger.py` validates source URLs against an approved HTTPS host allowlist, rejects unsafe URL schemes and duplicate record IDs, escapes HTML attributes/text, and generates unique instance-ID markup.
- WordPress.com Atomic **staging-only** shortcode plugin candidate: `[fv_ex2_research_desk]`, with prebuilt trusted static HTML, CSS and JS. The plugin is not installed, and direct post-shortcode detection has known limitations for widgets/reusable templates.
- Additional local Experience Lab overview/gallery linking Apollo 1 narrative, Research Desk and Evidence Atlas.
- Integrated `verify_all_v3.py` runner and `QA_V3_MANIFEST.json` per-file hash record.

## Evidence actually obtained

- Browser-tested in local Chromium at widths 360, 390, 768, 1024, 1440, 1920. Source search, empty results, count updates, native details (including no-JS), absent script state, multiple independently filtered instances, no horizontal overflow: PASS.
- PHP syntax: PASS.
- Existing Apollo 1 narrative, Atlas, concept board regressions: PASS.
- Deterministic duplicate packaging confirmed byte-identical.
- Full package `Final_Vestige_Experience_2_Foundation_v3.zip`: 82 files, SHA256 `ef9cb075f6b1903c92843500e09000032dcd81f5d4ce32466cf85ce8534328f6`.
- Isolated WP staging plugin ZIP SHA256 `8c7afa3378734891ab77e7818d3ccec8d328ef122b03710c1d24bf5467f2ac05`.
- Prototypes are **not** a substitute for actual WordPress staging tests, loaded NASA image visual QA, rights clearance, manual WCAG / screen-reader validation, Safari, 75p CWV, or hosted CI.

## Attached artifact handoff

The new executable code, screenshot sets, detailed QA results, source manifests, and WordPress adapter files are bundled in the conversation-delivered ZIP above; those source bytes are NOT committed to this research branch. A later Claude session should request the exact ZIP, not reconstruct the source from this outline. The WordPress candidate is solely a validation target, NOT an authorization to install it.

## Next steps

1. Founder selects art direction (Black Dossier is only the proposed starting point).
2. Run real WordPress.com Atomic **staging** integration with site theme and actual plugin stack, preserving production features.
3. Audit NASA media rights/delivery and source-to-claim crosswalk.
4. Capture loaded-image screens and test iOS Safari, NVDA/VoiceOver and zoom; run axe-core and field Core Web Vitals.
5. Implement formal source-content synchronization or versioned editorial review (snapshot may stale).
6. Work on a separate scoped implementation PR, with independent QD and green CI on exact SHA before any governed release.

**DO NOT touch PR #49 from Experience 2.0 R&D.** It has its own release issues and gates.