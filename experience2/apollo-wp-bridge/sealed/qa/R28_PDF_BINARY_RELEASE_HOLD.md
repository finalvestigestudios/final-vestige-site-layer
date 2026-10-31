# Apollo R28 — PDF binary safety and source-custody QA

**DRAFT / RELEASE HOLD.** Stacked on Apollo R27 PR #352 at exact SHA b03881c3414988c736e9c0da78b3462ddb1d7123. Scope is only experience2/apollo-wp-bridge/sealed/qa. Homepage PR #49, Research Desk PR #158, the WordPress site and all NASA evidence records remain unchanged. No image is reproduced, no Atlas geometry added.

## Why this exists

R27 verified tagged PDFs and their visible URL annotations, but its PDF metadata check did not inspect other active PDF features. A file could potentially contain an embedded attachment, hidden PDF launch action, document-level JavaScript, form, or non-link annotation without those showing in pdfinfo -url. R28 closes that specific QA gap for the existing offline evidence exports.

## Implemented guard

The new read-only pdf_binary_security_r28.py uses pypdf 5.9.0 and Poppler pdfdetach to inspect the actual PDF object graph, structure tree and parent tree, language, descriptive title preference, annotations, image streams, encryption and attachments. It rejects extra or missing links, non-NASA domains, JavaScript, launch/remote actions, file attachments, forms, missing tags and any inconclusive attachment inventory. Allowed PDF destinations: exactly six pinned NASA photograph source URLs, the Apollo 204 Review Board report and NASA media-use policy. All six photos remain link-only and rights review remains open.

The negative-control test_pdf_binary_security_r28.py requires a REAL R27 Chromium PDF input; it refuses to run without one. Tests deliberately mutate the binary to inject forbidden features. The build_r28_qa_archive.py script hashes and validates all seven R27 PDFs plus two PDF-rendered PNGs against the original R27 SHA256_MANIFEST.json, verifies each R28 audit receipt, and builds fixed-order, fixed-timestamp deterministic ZIPs. It does not pretend that independently regenerated Chrome PDF bytes are deterministic.

## Reproduce from exact GitHub checkout

Install Python pypdf==5.9.0 and Poppler pdfdetach. First generate PDF artifacts with the existing R27 browser runner. Then execute:

    FV_R28_PDF_FIXTURE=experience2/apollo-wp-bridge/sealed/qa/r26-pdf-evidence/apollo-r26-custody-390.pdf python -m unittest discover -s experience2/apollo-wp-bridge/sealed/qa -p test_pdf_binary_security_r28.py -v

    python experience2/apollo-wp-bridge/sealed/qa/pdf_binary_security_r28.py experience2/apollo-wp-bridge/sealed/qa/r26-pdf-evidence/*.pdf

To build the custody archive, use the build_r28_qa_archive.py --help options with the original R27 archive manifest, PDFs/PNGs, R28 binary report and mutation-test log. Do not substitute unverified PDFs.

## Executed results — October 31, 2026

- Original R27 exact GitHub head: b03881c3414988c736e9c0da78b3462ddb1d7123; original QA archive SHA-256: 4bcca3fc61fae14f0d0a0e60c7461597b9e0bc09952d51437f23fd0f54afbdb6.
- **7/7** original Chromium-tagged PDFs passed binary graph audit, covering prior viewport labels 320, 360, 390, 768, 1024, 1440 and 1920. Each has three pages, six photo annotations, two report/policy destinations, zero embedded images, zero attachments, and no reachable forbidden active actions.
- **21/21** real-PDF clone/mutation tests passed, including hidden links, JavaScript/open actions, launch, attachments, forms, missing tags/language and altered source annotations. Same **21/21** passed with python -O, verifying this security gate is not silently disabled by optimized Python.
- The earlier untagged R26 PDF is correctly refused for lacking a PDF structure tree. Two QA ZIP builds were byte-identical with identical input artifacts.
- This sprint DID NOT generate new PDFs with Playwright; it independently audited the seven real Chromium exports from R27. Local attempts to navigate Chromium to localhost and to a synthetic HTTPS origin both returned ERR_BLOCKED_BY_ADMINISTRATOR, so HTTP-enforced CSP/cookie and real WordPress testing were not claimed.

## Nonwaivable release blockers

Real installed WordPress/Assembler staging, HTTP CSP/cookie and nonce checks, independent verified axe-core, Safari and screen readers, PDF/UA manual accessibility testing, hosted LCP/CLS/INP and performance, per-photo rights review, unresolved S67-19766 catalog discrepancy, independent QD, green GitHub CI and explicit founder deployment authorization. **HOLD: No production writes or merges.**
