# Apollo R88 — Comparative Research Reading Room (STAGING HOLD)

Independent Experience 2.0 implementation built from the actual Research Desk, generated Evidence Atlas and frozen R37/R79/R55 NASA custody registers, through R86 cross-component concordance and R87 photograph-date validation. No homepage PR #49, Research Desk PR #158, main or production WordPress changes. Not a production plugin, site page or deployable release.

## Interaction and claims

Six complete source-linked EvidencePlates have native keyboard/no-JS SourceDrawers, provenance, credit, precise NASA URL, evidence limits, and jump links to verified photograph-date rail records. Optional progressive JS-only two-source comparison contrasts metadata, not alleged relationships. Third selection displaces oldest; Clear restores state; polite status announces changes. Without JavaScript all six original cards and sources remain available and compare controls hidden.

The S67-19766 crew-portrait association is provisional and dated only to January 1967; not assigned a fabricated day. Both January 24, 2017 photographs share a date without verified intraday order. Photograph dates are not a reconstruction of the January 27, 1967 fire. All photos are links only; zero rights cleared, embedded images, invented geo pins, or map edges.

## Reproducibility

From repository root:

    PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s experience2/evidence-atlas/tests -p test_reading_room_r88.py -v
    PYTHONDONTWRITEBYTECODE=1 python experience2/evidence-atlas/tools/build_reading_room_r88.py /tmp/fv-r88 /tmp/FV_APOLLO_R88_A.zip
    PYTHONDONTWRITEBYTECODE=1 python experience2/evidence-atlas/tools/build_reading_room_r88.py /tmp/fv-r88 /tmp/FV_APOLLO_R88_B.zip
    cmp /tmp/FV_APOLLO_R88_A.zip /tmp/FV_APOLLO_R88_B.zip
    PYTHONDONTWRITEBYTECODE=1 python experience2/evidence-atlas/tests/browser_reading_room_r88.py --src /tmp/fv-r88 --out /tmp/fv-r88-evidence --axe /path/to/axe.min.js

Dedicated exact-head CI pins Chromium/Playwright and axe; tests 320,390,768,1440,1920 widths with/without JS, native Enter disclosures, compare, touch, forced colors, reduced motion, overflow, screenshots, native print, local LCP/CLS and axe. Local lab timings are not hosted Core Web Vitals.

## Release blockers

Six individual NASA photographic-use assessments pending (including third parties, recognizable people, insignia, no endorsement). Hosted WordPress.com isolated acceptance not available, manual NVDA/VoiceOver/iOS Safari and physical device/zoom, independent QA and founder approval pending. Intermittent nested-Gutenberg LCP failure root cause unresolved. DO NOT MERGE OR DEPLOY.
