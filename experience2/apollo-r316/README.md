# Apollo R316 — accessible native keyboard menu continuity (STAGING ONLY)

Parent engineering [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), business [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Based exclusively on Apollo R315 draft PR #2229, not frozen homepage PR #49 or Research Desk PR #158.

## Reproduced defect and implementation

Real Chromium keyboard focus on the free Apollo investigation anchor followed by **Shift+F10** or **ContextMenu** dispatched a *trusted* native `contextmenu` with `button=-1, buttons=0, detail=0`. R315 only accepted right mouse button 2, so these keyboard-only interactions left the URL untagged even when the four existing, strictly validated Apollo campaign fields were present.

R316 accepts the observed keyboard event shape in the existing capture-phase handler, without preventing browser defaults, requesting a network resource, creating a cookie, adding a second CTA or changing NASA links. Synthetic and pre-canceled events remain blocked. PHP server-rendered HTML is still byte-identical across visitor query strings. No-JavaScript readers retain the actual free investigation link.

**Reproduce:** `python experience2/apollo-r316/qa/source_controlled_gate.py` (requires PHP, Node, Python `playwright` and `bs4`, installed Chromium at `/usr/bin/chromium`). Test authentic prior R315 bytes pinned to Git blob `b51975a674dd08e4dbba90b5a33a3d0efac68cd6`. Real browser proves the negative control misses *both* Shift+F10 and ContextMenu before R316 passes.

## Evidence and restrictions

Offline Chromium only: 320–1920px, JavaScript enabled/disabled, reduced motion and forced colors, screen width check, source custody (3 documentary references + 4 contextual photo catalogue records per instance), multi-instance isolation and query-independent PHP. Extended local testing additionally tests right-click mouse behavior, malformed/PII-like parameter rejection, synthetic/canceled events, old query cleanup, 200% text, CSS/no-JS failure, screenshots and fixture PerformanceObserver LCP/CLS. Screenshots and machine-readable receipts are in a separate deterministic run artifact; they are **not** production performance or hosted CI evidence.

**Unresolved mandatory gates:** actual installed WordPress/Assembler, real browser HTTP/CSP and CDN, genuine axe-core, independent screen readers, mobile native menu-item navigation, independently checked NASA media rights/editorial, consent, QD, successful hosted CI and founder release approval.

**Grok TASK-008 conflict:** the established general campaign uses `history_pilot_2026_11` with a real immutable asset ID, while this still-unapproved Apollo experiment validates `apollo1_pilot_2026_11` and an Apollo/platform-specific synthetic ID shape. Do not silently broaden accepted campaigns or claim real creator attribution; get an actual published Apollo asset_id and reviewed naming decision from Grok/Praxxis and Claude before shipping. No payable Apollo-aligned rights-cleared product or merchant-settled conversion has been authenticated. **No sale, lead, commission or net revenue is inferred from a URL annotation.**

**Release:** DRAFT / HARD HOLD / no WordPress or social/merchant writes.
