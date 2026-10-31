# Apollo Experience 2.0 R19 — Atlas Publication-Custody / Geographic Admissibility

**2026-10-31 — DRAFT / HOLD — Issue #150.** Stacked exclusively on Apollo R18 PR #294, immutable parent `cbcf3e576decbe7df624551d68761fe51996f075`. Canonical NASA evidence source remains PR #215 `74375657f2cdaac0710f94c6de6c24534ee06858`; Research Desk PR #158 and frozen homepage PR #49 are not changed. No WordPress writes or deployment.

## Implementation

- Six existing *publication references* are parsed from the exact pinned Atlas fragment with Python stdlib HTMLParser and independently compared against six hardcoded post-ID/theme/title/URL witnesses. **No coordinates or geographic relationship evidence have been approved.**
- Reject any new Atlas geo attributes, pinned publication URL/title/ID drift, unsupported seventh record, hidden "No mapped location" note, embedded images/iframes/svg/canvas/scripts or event handlers.
- Source-pinned, native keyboard/touch/no-JS disclosure inside the actual Atlas, six explicit "NOT REVIEWED" geography states, and link-only original published references. Responsive to 320–1920px, including 420px WordPress content block.
- Private JSON custody export with null coordinates, empty edges/media arrays, six post IDs, SHA-256 source provenance and no live-HTTP or historical-geocoding claim. Private PHP endpoint binds the sixth download to authenticated editor+nonce; page emits hash headers; read-only staging auditor checks served source and panel digests and all six exports.
- No NASA photo bytes, invented pins, map lines, URL changes to published investigations, or interaction with WordPress.

## Locally executed, not certifications

- Python/PHP tests **104/104 passed**; 14 new Atlas and adversarial cases.
- Real Chromium Playwright in-memory renders: exact page **7/7** (320,360,390,768,1024,1440,1920), new Atlas **7/7**, R17 dual-witness **7/7**, R18 Research Desk crosswalk **7/7**, R16 CDP accessibility-tree **7/7**. Native keyboard, touch, no-JS, reduced-motion, 420px embedded reflow and no horizontal overflow.
- PHP lint passes; real PHP local HTTP requests use a **synthetic WordPress authorization stub**.
- Two identical staging builds SHA-256: `4619b6acf31c9b8721e22a56aa43f9e745842467e2eded0f52e54f1fc3b04f64`. Generated plugin PHP SHA-256: `a721a45aea60654fbecb0c4b620a5dc47ea5119003457f0bce139017e4dcd640`.
- In-memory synthetic LCP where measurable: 280–1096 ms, missing at 1440px; synthetic CLS observed 0. **Not production Core Web Vitals.** No actual INP measurement.
- Strict axe-core gate **fails closed** without locally verified and SHA-256-pinned bundle. No axe/WCAG 2.2 AA certification claimed.

## Non-waivable release blockers

No installed local/hosted WordPress Assembler/Jetpack integration, because browser navigation to loopback is blocked by policy (`ERR_BLOCKED_BY_ADMINISTRATOR`). No browser-enforced HTTP CSP/cookie/frame-ancestor proof, actual axe audit, Safari/VoiceOver/NVDA, hosted CWV, successful CI on this exact head, independent QD, founder visual signoff, individual NASA media-rights clearance or definitive NASA catalog identifier for the Research Desk's S67-19766 label. The official NASA photo article describes the January 1967 training photo but does not show that accession in the visible copy; the PR158 editorial hold remains.

**DRAFT/HOLD. Do not merge, install, publish or deploy.**

Sources: https://www.nasa.gov/mission/apollo-1/ ; https://www.nasa.gov/image-article/apollo-1-crew-honored/ ; https://www.nasa.gov/nasa-brand-center/images-and-media/

Reproduce from `experience2/apollo-wp-bridge/sealed/`: `python -m unittest discover -s qa -p 'test_*.py' -q`, `python qa/browser_exact.py`, `python qa/browser_atlas_r19.py`, `python qa/ax_tree_r16.py`, `python build_sealed.py --out R19-private-review.zip`, `python qa/browser_exact.py --require-axe` (should fail closed without a verified asset).
