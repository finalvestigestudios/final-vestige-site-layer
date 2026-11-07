# Apollo R180 — install-aware acceptance gate (STAGING ONLY)

Independent additive QA for #150, stacked on draft R179 #1338. **No edits to original Research Desk #158, homepage #49, WordPress content/settings, Grok's creator queue, merchant systems or live analytics.**

## What changed
Previous sprints established real-browser passes only on *source-derived HTML fixtures*. They repeatedly left installed WordPress, genuine axe-core, media transport, CSP and production-like page performance **untested**. `qa/gate.py` distinguishes a fixture from an actual approved staging URL and **forces HOLD in fixture mode even when all interaction checks pass**. Remote mode refuses production and mismatched hosts, requires a local genuine axe-core library, and checks WordPress theme DOM, actual image decoding, keyboard-safe search functionality, no-JS visibility, NASA source links, the source-uncertainty warning, the single original-investigation action, and absence of intrusive commerce. Six Chromium sizes (320/360/390/768/1440/1920px) plus a no-JS run produce screenshots, SHA-256 manifests, a JSON receipt and non-field LCP/CLS lab observations.

### Offline verification (not WordPress acceptance)

```bash
cd experience2/apollo-r180/qa
python -m unittest -v test_gate.py
python gate.py --fixture /path/to/R179-source-derived-offline-fixture.html --output /tmp/apollo-r180-lab
```

Fixture receipts MUST remain `HOLD` even if tests pass. The fixture is an independent local QA input and is **not committed as historical production content**.

### Installed WordPress test (only with separate staging permission)

```bash
python gate.py --url https://approved-staging.example.test/apollo/ \
  --approved-host approved-staging.example.test \
  --axe-js /absolute/path/to/verified-axe-core.min.js --output /tmp/apollo-r180-staging
```

The remote test **reads** the page but does not change CMS settings/content. It requires a verified local axe-core file (not shipped). Run only on an authorized isolated staging domain. Current code does not establish valid NASA promotional rights. `TECHNICAL_PASS_NEEDS_FOUNDER_RELEASE` is not permission to merge or deploy.

## Remaining blockers

- R178 adapter and R179 JS are replacement-only source candidates, **not** an assembled or installed plugin. Complete exact-source integration and Gutenberg shortcode/asset lifecycle testing are mandatory.
- No approved installed WordPress staging host or genuine axe-core file was available in this sprint. Actual WP, axe, media/CDN, CSP/FOUC, VoiceOver/NVDA, published-site LCP/CLS and hosted exact-head CI remain **UNTESTED**.
- The original Research Desk template contains NASA reference links but no actual `<img>` media. The image-delivery gate intentionally remains HOLD until a reviewed integrated gallery/media presentation is present. Image attribution is not commercial image rights.
- No verified paid Apollo educator SKU, live Grok asset IDs, confirmed checkout, orders, refunds, fees or qualified-human session denominator. Net revenue per 1,000 sessions is **NOT COMPUTABLE**.

## Conversion hypothesis and controlled next action

Potential high-intent audience: educators viewing a Grok Apollo 1 long-form investigation, with approved per-video `asset_id` + UTM landing inventory supplied by Grok/Praxxis. Research Desk and source-custody evidence lead to **one nonintrusive “Read original investigation”** link. A future original, licensed educator dossier may eventually be proposed, but is not a verified sellable offer. No unrelated affiliate CTA, artificial urgency or unverified attribution is introduced. #820 measurement must distinguish a link click from a paid sale.

**Status: SOURCE CONTROLLED / FIXTURE BROWSER QA ONLY / RELEASE HOLD.**