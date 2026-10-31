# Apollo R13 NASA catalog witness — staging-only editorial QA

Checked **2026-10-30** against NASA's public item pages. This is a source-metadata witness, **not** proof that the Apollo 204 Review Board's interpretation is complete, that every image is free of third-party rights, or that NASA endorses Final Vestige. No image bytes are reproduced, linked as hot images, or embedded in the private plugin.

| Record | NASA page and catalog context | Era / claim boundary |
| --- | --- | --- |
| 01 | [Apollo 1 Crew Honored](https://www.nasa.gov/image-detail/apollo-1-crew-honored/) — crew near LC-34, January 1967; NASA | Contemporary training photograph, not the fire or an oxygen reading. Recognizable crew members; promotional use remains unreviewed. |
| 02 | [S67-15717](https://www.nasa.gov/image-detail/amf-s67-15717/) — module transfer, taken January 3, 1967; JSC | Spacecraft preparations, not a pressure or oxygen measurement. |
| 03 | [S66-58038](https://www.nasa.gov/image-detail/amf-s66-58038/) — altitude-chamber crew rehearsal, October 18, 1966; JSC | Not the January 27, 1967 fire or telemetry. |
| 04 | [KSC-20170124-PH_KLS01_0164](https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/) — Apollo tribute mockup; NASA/Kim Shiflett, January 24, **2017** | Retrospective museum display, not a surviving 1967 fire image. |
| 05 | [S67-21294](https://www.nasa.gov/image-detail/amf-s67-21294/) — post-fire command-module interior, January 28, 1967; JSC | Damage context cannot locate the exact initiating electrical arc. |
| 06 | [KSC-20170124-PH_KLS01_0090](https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/) — redesigned hatch tribute display; NASA/Kim Shiflett, January 24, **2017** | A later exhibit, not footage of the 1967 accident; broader redesign must remain visible. |

NASA's [Images & Media Usage](https://www.nasa.gov/nasa-brand-center/images-and-media/) distinguishes informational use from implied endorsement, rights of identifiable people, underlying third-party copyrights and protected NASA marks. **Item-level commercial/promotional clearance remains HOLD**, including the astronauts' likenesses. Historical page URLs and captions were verified by browsing on the stated date, not by a revalidating network request from the offline builder.

## Reproduce on the exact source-controlled branch

From `experience2/apollo-wp-bridge/sealed` with Python, PHP and Chromium installed:

```sh
PYTHONPATH="$PWD/qa:$PWD" python -m unittest discover -s qa -p 'test_*.py' -q
PYTHONPATH="$PWD/qa:$PWD" python build_sealed.py --out /tmp/apollo-r13-a.zip
PYTHONPATH="$PWD/qa:$PWD" python build_sealed.py --out /tmp/apollo-r13-b.zip
sha256sum /tmp/apollo-r13-{a,b}.zip
PYTHONPATH="$PWD/qa:$PWD" python qa/browser_exact.py
```

Browser tests use a PHP-CLI WordPress authorization stub and Chromium `page.set_content`; **not native WordPress, browser-origin HTTP/CSP, production traffic or field CWV**. Strict axe-core still requires a separately authenticated, SHA-256-pinned bundle. Do not turn its absence into a PASS.

The staging build calls `audit_files()` **after** the 12 upstream source Git blob pins and existing claim/HTML/CSV safety gates. The emitted `SEALED_SOURCE_MANIFEST.json` includes `nasa_catalog_witness` with an independent witness hash and rights HOLD. All work remains isolated from homepage PR #49, Research Desk #158, production WordPress, and paid services. On the existing WordPress.com Personal plan, use a free local/Playground replica for further testing; a hosted WordPress.com staging clone is not presently provisioned.
