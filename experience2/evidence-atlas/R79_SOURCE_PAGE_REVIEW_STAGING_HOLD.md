# Apollo R79 — NASA official-page custody and source-only staging gallery

**Status: STAGING_HOLD. Never deploy, merge, install into WordPress, or claim photo rights on this evidence.** Tracks #150. Branch base is Apollo R78 draft #696 at `4b5ae82e6c246bb0591317cb263f69109202d603`; original Research Desk draft #158 and homepage PR #49 and homepage engineer's branches remain untouched.

## What R79 independently checked (2 November 2026)

This is an **editorial verification of the six official NASA *image-detail pages***, NOT an independent license, copyright clearance or verification of the photograph's original image binary. The audit captures page fields and page-revision dates; R37 remains byte-for-byte identical (original Git blob `ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea`).

| Evidence | Proposed catalog | Official NASA PIA field | Photograph date | Scope |
| --- | --- | --- | --- | --- |
| 01 | S67-19766 | **No explicit structured PIA displayed; PROVISIONAL** | Jan 1967, day unspecified | Preflight crew portrait; does not establish cabin conditions |
| 02 | S67-15717 | Verified on NASA page | Jan 3, 1967 | Spacecraft preparation; not oxygen measurement |
| 03 | S66-58038 | Verified on NASA page | Oct 18, 1966 | Altitude-chamber training; not fire or sensor trace |
| 04 | KSC-20170124-PH_KLS01_0164 | Verified on NASA page | Jan 24, 2017 | Retrospective tribute exhibit |
| 05 | S67-21294 | Verified on NASA page | Jan 28, 1967 | Post-accident damage; does not prove unique ignition |
| 06 | KSC-20170124-PH_KLS01_0090 | Verified on NASA page | Jan 24, 2017 | Retrospective redesigned-hatch exhibit |

Sources: [NASA crew portrait](https://www.nasa.gov/image-detail/apollo-1-crew-honored/), [S67-15717](https://www.nasa.gov/image-detail/amf-s67-15717/), [S66-58038](https://www.nasa.gov/image-detail/amf-s66-58038/), [KSC-0164](https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/), [S67-21294](https://www.nasa.gov/image-detail/amf-s67-21294/), [KSC-0090](https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/) and [NASA brand/media rules](https://www.nasa.gov/nasa-brand-center/).

**All six individual image-rights decisions: PENDING.** Page access, NASA origin or a PIA number is not an individual photographic reuse determination. No NASA photos are downloaded or displayed. No invented image, speculative coordinate, map pin or relationship edge exists. These are **photograph dates, not fire-event sequence**. The January 1967 crew photograph has unknown day; its position within the month is deliberately not claimed precise.

## Source-controlled staging implementation

- `sources/R79_NASA_PAGE_AUDIT.json` stores a strict 15-field review per record with explicit provisional identity and reuse status.
- `tests/build_nasa_gallery_r79.py` gates its original R37 crosswalk by exact Git blob SHA, checks every audited NASA field and approved HTTPS URL, escapes all rendered values, outputs a self-contained HTML gallery with six source plates, a photograph-only chronology rail, **native** keyboard/touch/no-JS `<details>` SourceDrawers, and complete print custody.
- `staging/r79-source-review.css` provides scoped isolated gallery styles, 320–1920 layout, keyboard focus, 48px source and summary controls, forced-colors and reduced-motion support, and print copies even if closed disclosure content is hidden by Chromium.
- `tests/test_nasa_gallery_r79.py` tests 20+ adversarial source/permission/date/URL/geo/identity changes, no image or script, and byte-identical repeat builds.
- `tests/browser_nasa_gallery_r79.py` executes real Chromium on 320, 390, 768, 1440 and 1920 pixel viewports with JS/no-JS, touch, keyboard, reduced-motion and forced-colors, screenshot receipts, a native printed PDF, six catalog and rights text checks, browser error/overflow/network rejection, optional same-run pinned axe, and honest lab LCP/CLS readings.
- `.github/workflows/ex2-apollo-r79-nasa-pages.yml` requires a **clean exact GitHub PR head** before building reproducible artifacts; runs browser with **real localhost navigation and pinned axe-core 4.14.0 as required**, never optional. CI must pass and artifacts be independently inspected; a configured workflow is not itself a pass.

Local test runner:
```sh
python -m unittest discover -s experience2/evidence-atlas/tests -p test_nasa_gallery_r79.py -v
python experience2/evidence-atlas/tests/build_nasa_gallery_r79.py --repo . --out /tmp/R79_SOURCE_REVIEW.zip
python experience2/evidence-atlas/tests/browser_nasa_gallery_r79.py --repo . --out /tmp/R79_BROWSER --chromium /usr/bin/chromium
```

Local browser security policy can reject local navigation. A fallback `page.set_content` still tests actual Chromium DOM/rendering and native printing but **MUST report null LCP/CLS and does not imply live-navigation or hosted performance acceptance**. No local axe claim unless a pinned bundle is explicitly provided. Exact-head GitHub CI intentionally fails rather than silently making that fallback.

## Release gate

Existing R78 authentic disposable WordPress/Assembler acceptance and its axe results remain independently recorded; R79's new source-only static gallery is **not installed into WordPress** and carries no hosted WordPress.com compatibility claim. Production CWV at p75 and NVDA/VoiceOver, physical device, QD review, individual NASA media reuse decisions, the provisional S67-19766 association and founder publication authorization remain **HOLD**. Do not merge, publish or change CMS settings. Coordinate only via issue/PR comments with the homepage lead; no edits to frozen PR #49.
