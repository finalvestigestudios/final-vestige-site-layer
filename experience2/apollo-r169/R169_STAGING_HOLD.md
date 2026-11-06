# Apollo Experience 2.0 — R169 source/visitor-journey custody gate (DRAFT / HOLD)

Parent: #150. Conversion charter: #820 / #818. Source control deliberately stacked on R168 draft head `dcc90435fdfaae3a6f77da9926b433019603fbce`. This is a **new staging-only isolated verification layer**, not a WordPress, checkout, Jetpack or social-production change.

## Why this exists
The R168 guard attests the full WordPress editor source and checks link *counts* after transforming the gallery. Equal link counts alone cannot detect a source retarget, affiliate insertion replacing an existing anchor, changed link rel, altered photograph alt text or misleading narration. Such regressions would sever the proof-to-purchase trust chain. R169 independently parses the before/after HTML and requires the original **ordered href, human-visible anchor labels, target, rel; archival image src/srcset/alt/size/loading metadata; original narrative except the one justified context explanation; three official NASA citations; and Gutenberg boundaries** to remain unchanged. Any difference is a release HOLD. No product or affiliate link is introduced; an Apollo paid educator dossier is not a verified available SKU.

## Provenance and implementation
Reuses R168's exact WordPress Page 2017 raw-editor SHA-256 witness `6948f3d62d91d08c27a3a4b71122fef6ef37bdd333c31f81c27db4ad95ce5e4c` and the existing staged R167+R168 galleries. The three citation URLs match NASA catalog pages: S66-58038 (Oct 18, 1966 training), S67-15717 (Jan 3, 1967 spacecraft preparation), KSC-20170124-PH_KLS01_0129 (Jan 24, 2017 preserved hatch exhibit). The images are **context**, not timed photographs of the fire. No speculative Atlas pin/edge is generated. NASA's advertising/endorsement and likeness restrictions have not been independently cleared for paid promotion.

The HTMLParser gate is **not** a security sanitizer or an installed WordPress rendering proof. For a real release, rerun against a freshly read edit-context export; a different source SHA requires a new editorial and production review, not overriding the attestation. This module intentionally does not make network requests or write to WordPress.

## Reproduce
From the repository root, with Python 3.11+, playwright, Pillow, Chromium:

```bash
PYTHONPATH=experience2/apollo-r169:experience2/apollo-r168:experience2/apollo-r166 \
  python -m unittest -v experience2/apollo-r169/test_apollo_source_conversion_gate.py
```

The test imports R166 fixtures and R168 source custodian through PYTHONPATH. `CHROMIUM_PATH` may point to installed Chromium. Local tests completed **3/3 unittest methods twice**, including **eight intentionally tampered outputs rejected**. A total of **162 Chromium assertions per run** across 12 contexts: JS on/off at 320, 360, 390, 768, 1440, 1920px; reduced motion and touch emulation; keyboard Home; original source links and relevant investigation CTA. Six screenshots were SHA-256-identical across independent runs. The fixture inserts one original-investigation CTA before transformation; it does **not** prove the identical link is present in the actual installed page.

For an offline preview using the *real* pinned editor export only:

```bash
PYTHONPATH=experience2/apollo-r169:experience2/apollo-r168:experience2/apollo-r166 \
  python experience2/apollo-r169/apollo_source_conversion_gate.py /path/to/page-2017-edit-context.txt /path/to/preview.html
```

The generated JSON receipt is explicitly `approved_for_publish=false`, `commercial_activation=HOLD_NO_VERIFIED_APOLLO_OFFER`, and `wordpress_writes=0`.

## Evidence boundaries and release gate
**BUILT; OFFLINE CHROMIUM TESTED; NOT LIVE.** No installed WordPress page navigation: Chromium HTTP/data/file navigation returned `net::ERR_BLOCKED_BY_ADMINISTRATOR`; `page.set_content()` succeeded. No genuine axe-core (not installed and npm registry unavailable), real NASA CDN/image response, on-device screen reader, production CSP, installed-page LCP/CLS, qualified sessions, verified sales, Payhip orders or affiliate commissions. CI on exact GitHub head has not yet been confirmed. These missing checks are mandatory, not implicit passes.

### One contextual action and conversion hypothesis
Grok-owned long-form Apollo audience → the cited Apollo Evidence Atlas → **Read original investigation**, unchanged and nonintrusive. Hypothesis: maintaining exact-source links and an accurate chronology may improve reader continuation and future customer trust; no observed revenue or CTR supports the hypothesis yet. Do not insert a commercial offer until a matching rights-cleared SKU, price, checkout, delivery, consent/disclosure and merchant-paid order reconciliation are verified. Under #820, use asset_id / UTMs → qualified human sessions → relevant CTA → confirmed lead (if applicable) → independent merchant-confirmed paid orders → refunds/fees → realized net revenue, with 7/30-day cohorts and small-sample limits.

Release remains **STAGING HOLD** pending governed WordPress staging, real Playwright/axe/assistive-technology/CSP/CDN/performance acceptance, independent QA and Claude/founder deployment approval. Do not touch frozen homepage PR #49, Research Desk PR #158, Grok production, or Praxxis TASK-008.
