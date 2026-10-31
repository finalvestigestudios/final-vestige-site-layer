# Apollo R27 — tagged offline evidence PDF gate (DRAFT / HOLD)

The R26 PDF's source URLs and rights notices were correct, but Poppler reported `Tagged: no`. R27 generates PDFs with Chromium `tagged=True, outline=True`, then independently inspects the **actual PDF bytes**. `pdfinfo` must report a descriptive Apollo/Final Vestige title, `Tagged: yes` and `JavaScript: no`. `pdfinfo -url` must show six **distinct clickable** photograph URLs from pinned casefile records, plus NASA's Apollo 204 report and media guidance, with **zero unknown or non-HTTPS URL annotations**. Existing PDF text continuity, six rights HOLD notices, source fingerprints and zero embedded-image checks are preserved.

**Local real-browser evidence:** exact R26 private PHP plugin SHA-256 `bb0d8a2493fabee4a852a200d7d67b5b1421c5dc29317d21a795763cf54f6c13`; PHP loopback returned 222,573 HTML bytes with a synthetic editor nonce, then Chromium rendered them through `page.set_content` with JavaScript disabled. Seven real A4 PDFs at 320/360/390/768/1024/1440/1920px: **7/7 passed**, three pages each, structural tags present, six photo links, two NASA policy/report link destinations, ten annotations, zero unapproved origins, zero embedded images. Ten adversarial Python tests: **10/10 passed**, including explicit rejection of the old untagged sample.

**Reproduce from a complete checkout** (Chromium, Playwright, Poppler, PHP):

```bash
python -m unittest discover -s experience2/apollo-wp-bridge/sealed/qa -p test_pdf_semantics_r27.py -v
python experience2/apollo-wp-bridge/sealed/qa/browser_pdf_r26.py
pdfinfo experience2/apollo-wp-bridge/sealed/qa/r26-pdf-evidence/apollo-r26-custody-390.pdf
pdfinfo -url experience2/apollo-wp-bridge/sealed/qa/r26-pdf-evidence/apollo-r26-custody-390.pdf
```

**Boundaries:** Only Apollo QA code, parent R26 PR #344 commit `12ccf28b6a3cd32931cbe321fddff07b9c5cd4eb`. Verified local/committed blobs: PDF runner `0492fd378edd8555d6b317adb22000ca6bf91d01`; regression test `59ddaac7634951cd272266aa59e08c57a07caff2`. No media licenses claimed; `S67-19766` identity unresolved; zero speculative map pins. Frozen homepage PR #49, Research Desk PR #158 and live WordPress untouched.

**Release HOLD:** Browser navigation to localhost returned `ERR_BLOCKED_BY_ADMINISTRATOR`; tests used PHP HTTP retrieval + Chromium `set_content`, **not browser-enforced CSP/cookies** or real WordPress. Tagged export is not PDF/UA or screen-reader certification. Axe, Safari, authenticated independent staging, hosted performance, NASA reuse decisions, catalog resolution, independent QD, passing CI and founder approval remain outstanding. Browser PDF bytes may vary with Chromium metadata; deterministic sealed source build unchanged. No merge/deployment.
