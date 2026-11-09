# Apollo Experience 2.0 — R237 immutable evidence + conversion gate

**DRAFT / staging hold only.** This lane makes no homepage (#49), Research Desk (#158), production WordPress, Grok content, analytics, commercial, or paid-service changes. This is a separately stacked child of Apollo R236 PR #1734, not a merge request to main.

## Scope and reproducibility

The executable `qa/release_gate.py` hard-pins the complete R236 generated manifest SHA-256 `f9169870eb3c02415feaf70eed9bbefdca5b194c6ddb27a92a0b80102ef1ce95` and HTML template SHA-256 `50dbe79bbb223762a01614e52fd7a5098784a7d2bd04ceadd2ac69cdf43d3bb6`. It checks every manifest-file checksum, the four NASA records' claim limits and link identities, the one free article CTA, and the unapproved-commerce/creator-asset gates. Eight adversarial mutations must be rejected using the *same* validator, not just compared to an arbitrary reference string.

With local Python + Playwright + Chromium (`/usr/bin/chromium`), use an independently verified R236 build:

```sh
python experience2/apollo-r237/qa/release_gate.py --out /path/to/generated-r236 --qa /new/path/qa-A
python experience2/apollo-r237/qa/release_gate.py --out /path/to/generated-r236 --qa /new/path/qa-B
```

Each run checks 320, 390, 768, 1440, and 1920 pixel widths with JavaScript on/off, touch/keyboard native disclosures, reduced motion, forced-colors fixture, unique source action names, correct CTA, IDs/anchors, overflow, and unwanted network requests. It writes screenshot SHA hashes, deterministic receipt JSON, and *separate variable* local LCP/CLS sample JSON. Exact screenshot and receipt identity should be checked between independent runs.

Optional `--axe-core /local/reviewed/axe.min.js` injects genuine axe-core and fails on reported WCAG violations. Without that argument, axe is **NOT RUN**. The script intentionally makes no external downloads.

## Release gate / business decision

Offline `page.set_content` Chromium fixtures are NOT installed WordPress, real HTTP navigation, screen-reader acceptance, actual browser UI zoom, field performance, audited media rights, or verified monetization. In this runtime localhost HTTP is blocked with `net::ERR_BLOCKED_BY_ADMINISTRATOR`; hosted CI and independent QA still required. Existing R198 source ancestry remains unresolved. No source, feature, or commercial release authorization is implied.

**OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER:** Apollo educator evidence dossier is only hypothetical, with no approved SKU, rights, merchant orders, price or fulfillment. A not-yet-proven Grok documentary could bring qualified history viewers to the NASA-backed Atlas and its single free original-investigation CTA. The gate blocks injected purchase links, fictional orders/UTMs and unsupported source claims until rights/checkout and authentic creator asset IDs can be verified. Apollo owns this isolated gate; Grok owns social production, Praxxis independent creator review, Claude production engineering/analytics, and founder release approval. Net revenue per 1,000 qualified human sessions (7/30-day cohorts) is **NOT COMPUTABLE** without qualified traffic and verified paid-order/fee/refund evidence. Never equate clicks or leads with sales.

Reference: #150 / #820 / #818, original Research Desk #158. No speculative geo pins, fake evidence, copied NASA branding, affiliate activation, social posting, emails or spending.
