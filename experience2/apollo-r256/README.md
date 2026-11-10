# Apollo R256 — Print custody of collapsed NASA SourceDrawer (staging only)

**Purpose.** The sealed R238 Apollo Atlas contains a native `<details>` SourceDrawer holding four source-provenance records. Chromium's *Print* view omitted the entire body when the reader had not first expanded the drawer. That loses the report-vs-photograph distinction and source limitations from a saved research packet. R256 adds a print-only stylesheet; the original NASA data, document links, gallery, chronology, HTML and screen presentation are unchanged.

## Verified negative control and correction

From the original sealed R238 PHP output (manifest SHA-256 `f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68`), the closed drawer previously printed **0** records with a "Source kind" field, versus **4** after the R256 overlay. The fully opened drawer still prints **4** records. Its source names are Apollo 204 Review Board, S66-58038, S67-15717 and S67-21294. This is an archival usability improvement, **not** new media clearance.

## Reproduce offline

The test relies on Python Playwright, `/usr/bin/chromium`, `php` and `pdftotext`, plus the sealed R238 fixture and parent R253–R255 CSS. It creates only local PDFs, screenshots and JSON receipts.

```sh
python experience2/apollo-r256/qa/qa_r256.py \
  --atlas /absolute/path/to/sealed-r238 \
  --r253 experience2/apollo-r253/atlas-source-actions.css \
  --r254 experience2/apollo-r254/provenance-tap-continuity.css \
  --r255 experience2/apollo-r255/evidence-path-touch.css \
  --overlay experience2/apollo-r256/print-custody.css \
  --out /tmp/apollo-r256-qa
```

The test checks the exact sealed manifest and PHP-rendered template, an actual Chromium negative print control, source text in `pdftotext` from generated PDFs, 320/390/768/1440/1920px with JS enabled/disabled, native keyboard/touch semantics, one free investigation CTA, no unexpected requests, no overflow, and byte-identical **screen** screenshots with or without the print-only overlay.

## Commerce bridge (not activated)

The single editorial action is the existing **free Apollo investigation**. A future teacher-ready evidence kit may be an appropriate optional *post-reading* offer for history educators, **only after** SKU, originality, rights, actual checkout/fulfillment, fees/refunds, media reuse, terms and founder approval are documented. Existing Products 001–015 have not been verified as matching that hypothetical kit. A Grok Apollo long-form `asset_id` and approved landing URL remain unverified. Never add unrelated affiliate pitches to the tragedy narrative. Funnel: verified asset → qualified human session → source review → free reading → optional approved offer → independently confirmed paid order → net receipts. Missing payment/attribution is not zero revenue; label it **unobservable**.

**RELEASE HOLD.** This is a CSS proposal, not an installation. No installed WordPress/Assembler, actual HTTP/CSP/CDN, browser-native UI zoom, independent screen reader, genuine axe-core, field CWV, hosted CI, external rights certification, commercial checkout or founder release approval is asserted. No edits to frozen homepage PR #49, original Research Desk PR #158, Grok queue, WP, analytics or revenue systems.
