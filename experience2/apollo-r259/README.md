# Apollo R259 — committed original-PHP browser acceptance (STAGING HOLD)

**Parent:** Apollo R258 draft PR #1876, exact parent `2a2651bd3ce2d8b125bd5e326612fb5f1a7bbb12`. Charter #150; conversion authority #820 / #818. No modifications to homepage PR #49, Research Desk PR #158, original Apollo material, NASA citations, public WordPress, Grok/Praxxis tasks, analytics, commerce or emails.

## What is actually implemented

`qa/atlas_acceptance.py` is a standalone, source-controlled Playwright runner. It checks the sealed original R238 manifest (SHA-256 `f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68`), every child source hash, runs the **actual PHP rendering shim**, and requires exact original HTML identity. CSS includes the existing R253–R257 accessibility/print layers, not a new visual product. It rejects external CSS dependencies and unapproved outbound requests.

Local execution in Chromium: **12 contexts per run** (320/390/768/1440/1920 with JS on and off; forced-colors at 390/1440), native SourceDrawer keyboard Enter/Space, mobile tap, reduced motion, one free original-investigation action, four NASA plates, 55 NASA hyperlinks, 31 local anchors, no detected horizontal overflow, and 92/92 expanded-state actions at least 44 × 44px across five widths. Four hero and four SourceDrawer screenshots per run are digest-checked. Two independent local executions produced **8/8 matching screenshot SHA-256 pairs** and identical stable receipts `7ad3227ebf3dd4864f1039470022be910cc20114ef5873f0c0b0b8e5f12df1af`. These are local observations, not production accessibility certification.

A deliberately tampered original CSS was correctly rejected by the exact child hash. `--require-axe` correctly returns nonzero without a provenance-verified genuine axe-core bundle: **genuine axe-core NOT EXECUTED**. To run genuine axe, provide a licensed/source-verified local `--axe-bundle /path/axe.min.js --axe-sha256 <verified_SHA256> --require-axe`; do not fetch or activate third-party scripts on the public site. This option is implemented but unexercised against real axe-core in this environment. No optional JS is necessary for the Atlas's 13 native HTML disclosures.

## Reproduction (no network)

```sh
python experience2/apollo-r259/qa/atlas_acceptance.py \
  --atlas /path/to/sealed-r238 \
  --overlays experience2 \
  --out /tmp/apollo-r259-qa
```

Dependencies: PHP CLI, Python 3, local Playwright package, local Chromium binary. The sealed R238 fixture is distributed separately in the founder's QA archive; it is **not** copied into this PR. The runner's deliberately isolated `set_content` mode is needed because this environment blocks browser navigation even to localhost. It cannot validate installed WordPress/Assembler, theme interactions, actual HTTP/CSP, CDN media, device zoom, WebKit/Firefox, manual screen readers or production CWV. In particular, the local Performance API returned **no LCP samples**; observed layout-shift entries summed to 0 and do not establish field CLS.

## Landing-to-product funnel and governance

**Audience:** verified interested Apollo long-form viewers, with educator intent as the commercial hypothesis.

**Path:** Grok-approved Apollo long-form asset (published asset ID still unverified) → source-led Atlas → **one existing free investigation** → optional, separately approved teacher-ready original-source case dossier only after matching a real sellable SKU, licensed pedagogy/media, functioning checkout/fulfillment and confirmed merchant reporting. No paid link or interest-collection form is added. WordPress read-only on Nov 10 confirmed the existing original investigation is published as post ID 434 at `https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/`; the external HTTP endpoint could not be independently retrieved by the browsing environment, so a public click-through/response check remains open.

**Revenue measurement:** by Grok asset ID and UTM campaign, report qualified human sessions, relevant CTA click, confirmed opt-in where applicable, actual paid orders and independently reported affiliate conversions, refunds/fees and realized net revenue per 1,000 qualified sessions in 7/30-day cohorts. **No qualifying published Grok Apollo asset, verified paid match, purchase, attributed session or net revenue was authenticated by this test.**

**Release hold:** genuine axe, independent screen-reader verification, hosted CI/QD, installed WordPress/Assembler browser tests, real HTTP/CSP, field CWV, commercial clearance, resolution of inherited R198 ancestry discrepancy, and explicit founder production approval. Do not merge, activate or deploy this QA-only PR without governance.
