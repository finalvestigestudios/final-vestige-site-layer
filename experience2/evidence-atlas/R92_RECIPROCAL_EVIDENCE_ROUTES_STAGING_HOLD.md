# Apollo R92 — Reciprocal, source-exact evidence navigation (STAGING HOLD)

**Isolated Experience 2.0 Apollo 1 R&D. NOT APPROVED FOR PUBLICATION.** Built atop R91 and the actual R90/R86 Research Desk / Evidence Atlas custody gates, independent of frozen homepage PR #49, lead homepage branches and original Research Desk PR #158.

## Actual user-facing defect corrected

R89's evidence hub links each of six NASA records to the corresponding Research Reading Room, photograph-date ChronologyRail and NASA photographic-rights board. The three destination views do not contain a reciprocal, direct path to that **same record** in all other views. Users landing on a deep link must leave the record and search again.

R92 adds **54 source-specific native links**, three per record × six records × three destination views, complementing 18 existing hub routes (**72 same-record links across four views**). All paths and fragments are checked against the matching source identity. This is an editorial navigation relationship between depictions of the **same** research record, not a historical connection between separate records. No invented geospatial pins or relationship edges.

New HTML `<nav aria-label="Other evidence views for source NN">` works without JS. Scoped CSS provides 44px touch targets, visible keyboard focus, single-column 320px layouts, forced-colors adaptation, and print suppression of navigation (original evidence limitations, individual NASA URLs and rights warnings remain printable).

## Actual build and provenance

`tools/build_reciprocal_routes_r92.py` invokes the **real R91 builder** on a disposable directory, checks the inherited asset allowlist, inserts reciprocal routes into exactly six evidence cards in each of three views, re-runs R91 asset custody over the **changed** HTML and CSS, updates cryptographic receipts to match actual bytes, and checks every NASA link and every route target before exporting. The resulting staging package has a deterministic sorted ZIP and SHA-256 manifest including exact source-controlled scripts, tests and CI definition.

Fail-closed mutation testing covers 15 positive/adversarial cases: wrong-source routing, duplicate and missing routes, path escape, `javascript:` URI, NASA link swap, unexpected photo, remote stylesheet, duplicate IDs, altered inherited receipt and falsely cleared image-rights metadata.

The isolated R92 Actions workflow runs 40 genuine Chromium contexts (four views × 320/390/768/1440/1920px × JS on/off), 40 real cross-document link navigations, native Enter/Space source disclosure, touch, reduced-motion and forced-colors testing, eight axe-core WCAG-tagged scans, local LCP/CLS checks, screenshots and four native PDFs verified to retain all six exact NASA destinations.

## Reproduction at exact branch HEAD

```bash
python -m unittest discover -s experience2/evidence-atlas/tests -p test_reciprocal_routes_r92.py -v
python experience2/evidence-atlas/tools/build_reciprocal_routes_r92.py /tmp/r92-a /tmp/r92-a.zip
python experience2/evidence-atlas/tools/build_reciprocal_routes_r92.py /tmp/r92-b /tmp/r92-b.zip
cmp /tmp/r92-a.zip /tmp/r92-b.zip
# Browser CI: .github/workflows/ex2-apollo-r92-reciprocal-routes.yml
```

Exact-head CI must be green before claiming acceptance. The source build and 15 mutation cases were locally checked against the archived genuine R91 artifact; local Chromium rejected all navigation via an environment-level policy (`ERR_BLOCKED_BY_ADMINISTRATOR`), so a passing GitHub Actions Chromium run is necessary before counting real-browser acceptance.

## Release blockers and non-goals

No NASA photos reproduced, photographic reuse clearance **0/6**, crew portrait catalog `S67-19766` remains provisional. Research chronology does not reconstruct the January 27 fire; two January 24, 2017 photos have no claimed sequence. Hosted WordPress.com isolated compatibility, physical-device testing, manual NVDA/VoiceOver, independent QA, intermittent Gutenberg LCP investigation, production CWV and explicit founder release approval remain open.

**No merge, no production WordPress or settings writes, no deployment, no paid services.** R92 is a source-controlled staging candidate only.
