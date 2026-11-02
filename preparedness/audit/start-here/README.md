# Start Here: audit files

Reproducible evidence for the four Start Here articles and the two tools. Nothing here is a human review, and nothing here sets `human_link_check`.

| File | What it is |
|---|---|
| `claims.json` | Hand-written claim-to-source matrix (69 rows: 63 with a source, 6 editorial). Each row has short anchor phrases, the location in the source, the basis (direct / synthesis / interpretation / editorial), confidence, limits and who must review. |
| `verify_sources.py` | Re-fetches every source cited by the four articles (Playwright with Microsoft Edge for pages; PDFs through Playwright's request API and `pdftotext`) and checks the anchor phrases. Writes `ledger.json` and `claim-matrix.json`. |
| `ledger.json` | Per source: HTTP status, final URL, title, page-stated dates, text length, SHA-256 of the normalized text, and per-claim anchor results. |
| `claim-matrix.json` | `claims.json` merged with the automated results. |
| `render_audit.py` / `SOURCE-AUDIT.md` | Human-readable tables generated from the two JSON files. |
| `qa-evidence.json`, `screenshots/` | Output of `tests/browser_qa_start.py` (366 checks, eight widths) and six compressed full-page screenshots (hub, both tools; 320 and 1440 px). |

## Reproduce (from the repo root)

```bash
python -I preparedness/audit/start-here/verify_sources.py      # ~70 s, needs network, Microsoft Edge and pdftotext
python -I preparedness/audit/start-here/render_audit.py
python -I preparedness/tools/build.py
python -I preparedness/tests/browser_qa_start.py                # ~45 s, writes qa-evidence.json and screenshots
```

## What an anchor check does and does not show

It shows that a short phrase from the claim's supporting passage is present in the page or PDF text fetched on the run date. It does **not** show that the article's paraphrase is faithful, that the whole document was read, that the page is current tomorrow (the ledger's text hash will change when the page does), or that a human opened the link. One claim (C21b: FEMA 2020 "at least 72 hours") cannot be confirmed by `pdftotext` because the sentence sits in a call-out box the tool does not extract; it was seen in the Firecrawl PDF parse of 2026-10-29 and needs a human to confirm on the rendered page.

Page text is held only in memory by the script; no source text is stored in the repository, only hashes and short anchors.
