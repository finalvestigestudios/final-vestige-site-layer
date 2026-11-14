# Apollo R352 — Source navigation semantics and screen-reader discovery

**BUILD ONLY — DRAFT / NOT LIVE / NOT LICENSED FOR COMMERCIAL IMAGES.** Stacked on R351 PR #2429 and independent of homepage PR #49 and Research Desk owner PR #158. Parent: #150; commercial coordination: #820, #818.

## Defect and correction

The previous ChronologyRail offered six identically named *Source and evidence limits* disclosures, the photo gallery four identical *Provenance and limits* disclosures, Board plates three identical custody disclosures, and the custody drawer eight indistinguishable *Open institutional source record* links. A screen-reader's flattened controls or links navigation could not determine which event, photograph, finding, or source page each controlled. The Evidence Index filter toolbar also placed `aria-label` on a generic div without a semantic grouping role.

R352 now gives **21 unique, visible, contextual disclosure names** (six chronology, four accession, three Board finding, eight custody) and **eight unique visible source-link names**. The filter toolbar receives `role=group` with its accessible group name. All names are escaped from the same reviewed source rows, preserving source-to-claim integrity and avoiding a new source authority. No new historical claim, URL, outbound commerce, NASA media, geo pin or analytics script is introduced. Existing single free-investigation continuation remains the only CTA.

## Acceptance

Run `python experience2/apollo-r352/qa/semantic_smoke.py` from the repository root with PHP, Python Playwright and Chromium installed at `/usr/bin/chromium`. It uses local PHP output and page.set_content; never touches a public website. It asserts 21 contextual disclosure names, eight unique custody link labels, filter semantics, no-JS display, keyboard Enter, and horizontal overflow at 320, 390, 768, 1440, 1920px (including 320px at 400% root type). This **is not genuine axe-core, assistive-technology acceptance, installed WordPress, browser-enforced HTTP/CSP or field Core Web Vitals**. Real axe-core, VoiceOver/NVDA, Firefox/WebKit, actual WordPress/Assembler, native HTTP/CSP, hosted exact-HEAD CI and QD/founder approval remain release gates.

## Source and rights boundary

The NASA 1967 Apollo 204 Review Board identifies an electrical arc as the most probable initiator, **not** a conclusively known individual ignition source: https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html . NASA's brand/advertising rules prohibit implied sponsorship and restrict insignia and certain commercial imagery: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . These links verify reference context, not media licensing or product approval.
