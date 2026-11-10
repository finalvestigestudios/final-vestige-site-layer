# Apollo Experience 2.0 R252 — exact NASA Atlas browser and printed-source acceptance

**STAGING HOLD / NOT LIVE.** Isolated additive QA on R251. No alterations to historical
record, NASA imagery, CSS, JS, Research Desk PR #158, homepage PR #49, WordPress,
analytics, email, Grok queue, offers, or paid services.

## Purpose and actual code

`qa/r252_browser_acceptance.py` renders the protected **R238 Apollo Evidence Atlas**
through the *original PHP adapter*, rejects any manifest/asset drift, and exercises the
actual HTML/CSS in Playwright Chromium at **320, 390, 768, 1440 and 1920 px**, with
JavaScript enabled and disabled. Checks are executable assertions, not screenshot-only
reviews: four NASA evidence plates, chronological markers, a named NASA citation
action in Chromium's accessibility tree, one free-investigation CTA, allowed destinations,
hash links/unique IDs, no unexpected network requests or horizontal overflow, keyboard
skip-link navigation, native `<details>` Enter/Space, and mobile tap.

Actual Chromium PDFs are parsed with PyMuPDF to verify that **at least 8 NASA URLs
and the archival rights index remain printable**. The PDFs are normalized to fixed
metadata for reproducibility. The runner writes hash receipts and 390/1440 screenshots.
Source-asset manifest is fixed at SHA-256
`f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68`.
It never downloads NASA images or changes a production site.

## Reproduction on isolated machine

Provide the exact R238 sealed `sealed-r238/` directory from the existing R251
evidence package; no external NASA/media fetch required.

```sh
python3 -m pip install playwright pymupdf
# PHP CLI and a locally installed Chromium are required.
python3 experience2/apollo-r252/qa/r252_browser_acceptance.py \
  --atlas /path/to/sealed-r238 --out /tmp/apollo-r252-A
python3 experience2/apollo-r252/qa/r252_browser_acceptance.py \
  --atlas /path/to/sealed-r238 --out /tmp/apollo-r252-B
sha256sum /tmp/apollo-r252-{A,B}/receipt.json
```

This source-controlled test expects Chromium at `/usr/bin/chromium`; explicitly
adapt path in a reviewed QA-only PR for other machines. Optional
`--axe-js /path/to/independently-verified/axe.min.js` exercises **genuine axe-core**
on JS-enabled contexts. Do not interpret that optional ability as evidence of
an executed axe run. Without the official bundle, receipt reports
`NOT_EXECUTED_MISSING_OFFICIAL_BUNDLE`.

## Evidence and limits (2026-11-09 PT)

A local *equivalent* original-PHP runner was executed twice on Chromium 144:
**10 contexts each, PASS**; 4 paired screenshots byte-identical, two normalized
PDFs byte-identical, 22 visible NASA URL occurrences per print output. Its receipts
matched on independent runs after timestamp normalization. The remote committed
script must still be run byte-for-byte against a full checkout before any release
gate can be considered satisfied; local exploratory execution is not a replacement.

HTTP navigation even with Playwright route mocks returns
`ERR_BLOCKED_BY_ADMINISTRATOR`, so actual test navigation is `page.set_content`,
not website HTTP/CSP. Browser AX tree is not genuine axe-core, nor a human screen-reader
test. No installed WordPress/Assembler acceptance, no Safari/Firefox/NVDA/VoiceOver,
no authenticated buyer/merchant checkout, no field LCP/CLS/INP, no verified paid
conversions, and no hosted CI are claimed. The unresolved inherited R198
source-ancestry discrepancy and independent review are release blockers.

## Commercial handoff without narrative contamination

Flagship: Apollo 1 historical evidence; high-intent audience: original-history
documentary viewers, educators and artifact enthusiasts. Flow:
**Grok verified Apollo long-form `asset_id`/UTM → Atlas sources → one free original
investigation CTA → separately approved contextually appropriate offer.**

Hypothesis: high-quality provenance and complete printable source records increase
qualified trust and progression, which *could* improve the eventual paid outcome;
this must be tested against paid order evidence rather than pageviews. Neither
Mini Museum acceptance/affiliate commissions nor an educator dossier SKU/rights/checkout
is verified. No paid CTA is inserted. Business success requires first-party
qualified-human sessions and confirmed merchant purchases, net of refunds/fees;
`1000 * realized_net_revenue / qualified_human_sessions` is **NOT COMPUTABLE**
with missing numerator or denominator. For 7/30-day cohorts warn on tiny samples.

**Owner plan:** Founder/Claude validates one truly sellable offer, merchant terms,
rights and checkout before activation; Grok owns production and posting, Praxxis
independent creator QA and TASK-008 inventory; Apollo owns isolated evidence UX and
browser QA; Claude owns production analytics and implementation. See #150,
#820 and charter #818. No publishing, sending, payments or release actions.


## R252 print-contrast defect, isolated correction and executable negative control

**Actual defect found:** the original sealed R238 Atlas printed 13 text spans with
white-paper contrast below 4.5:1, including the introductory `Evidence, not spectacle.`
line, confidence labels, NASA archival-source kinds, and teacher-lesson badges.
These inherited screen colors were extremely pale on printed white paper.

A new component-scoped `r252-print-custody.css` supplies a **print-only** `#111`
override for those six selectors. The original R238 manifest/CSS and all historical
text, source links and CTA remain unchanged. Nothing is installed in production.

**Exact committed test:** `qa/r252_print_contrast_gate.py` (Git blob
`ed2c635cc00432c91304a097512df9c021c59970`) was executed locally, byte
for byte, twice. It renders the original R238 PHP HTML with Chromium 144 to PDF
using the sealed original stylesheet, proves **13 failing spans**, adds the
isolated print override (Git blob
`11bb761b857253b84f636cd174ef32e25933a7e1`), and proves **0
low-contrast spans**, preserving 22 visible `nasa.gov` URL occurrences
and the archival rights index. The resulting 14-page normalized PDFs are
byte-identical across the two runs, SHA-256
`f6ff7d34c46a9b2def1263b6dd08168f4e6b557823b2f77fe6471b4db0004eb0`.

Reproduce against the sealed R238 package:

```sh
python3 experience2/apollo-r252/qa/r252_print_contrast_gate.py \
  --atlas /path/to/sealed-r238 --out /tmp/apollo-r252-print
```

This compares extracted PDF text ink against *assumed white printed paper*.
It is not a full background-aware WCAG audit, genuine axe test, print-driver
matrix, real WP staging, or commercial release. The staging enhancement
must be reviewed and integrated through the owner's controlled build before
any production use.
