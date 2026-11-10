# Apollo Experience 2.0 — R254 source-action continuity

STATUS: STAGING HOLD, NOT LIVE. This adds an isolated overlay and executable Chromium test stacked on R253 PR #1844. The source-controlled original R238 NASA evidence, Research Desk PR #158, frozen homepage PR #49, WordPress settings, Grok queue, analytics, checkout and production are not changed.

## Observed defect

The R253 enhancement addressed 20 source anchors, but the broader exact-source audit revealed 47 visible NASA source links across the original rendered Atlas. With the sealed R238 CSS + R253 overlay, 3–12 of those 47 links had a click target below 44px depending on viewport. The R254 overlay gives all 47 visible NASA links a measured >=44px target at 320, 390, 768, 1440 and 1920 CSS px, with JavaScript enabled and disabled. A higher-specificity method-grid selector required its own explicit display correction.

The native SourceDrawer still uses keyboard Enter and Space; links still support touch and keyboard. Forced-color focus and a print reset are preserved. The sole original free-investigation CTA is unchanged; no affiliate or product link is introduced.

## Reproduce

Prerequisites: Python 3, Playwright for Python, PyMuPDF, PHP CLI, local /usr/bin/chromium and the sealed-R238 fixture from the Apollo R253 evidence bundle. The fixture manifest must SHA-256 to f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68; each child is hash-checked and PHP output must be byte-identical to its protected HTML template.

Command: python experience2/apollo-r254/qa/r254_gate.py --atlas /path/to/sealed-r238 --r253 experience2/apollo-r253/atlas-source-actions.css --r254 experience2/apollo-r254/provenance-tap-continuity.css --out /tmp/apollo-r254-A

Repeat with --out /tmp/apollo-r254-B, compare receipt.json SHA-256, screenshot SHA-256 and normalized PDF SHA-256. These are deterministic when reproduced in the same browser/runtime configuration.

Two completed independent local runs: 10 Chromium 144 contexts each; 47/47 visible NASA source links >=44px; source URLs and free CTA unchanged; 0 horizontal overflow; expected native keyboard and mobile tap; no external requests; 4/4 screenshot pairs and 2/2 normalized PDF pairs identical; adversarial missing-touch-rule mutation detected. Executed source CSS and Python script match committed Git blobs.

## Source and release custody

NASA Apollo 204 Review Board source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA advertising/endorsement restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . A probable electrical arc is NOT proof of the exact ignition point. Do not invent geospatial pins, media permissions, NASA endorsement or commercial facts.

Offline Playwright page.set_content is NOT installed WordPress HTTP acceptance. Genuine axe-core, Safari/VoiceOver/NVDA, browser-interface zoom, live CSP/HTTP, hosted CI, independent QA, inherited R198 ancestry discrepancy, NASA commercial-media rights and founder approval remain outstanding. This gate does NOT provide field LCP/CLS or qualified-session/paid-conversion metrics.

Related: Issue #150 (Apollo), #820 (verified attribution), #818 (business charter); creator Grok and Praxxis coordinate separately in TASK-008. Claude owns production code/analytics integration; founder retains release and spending decisions. STAGING HOLD.
