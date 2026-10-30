# Focus Complete Edition — PDF integrity evidence reconciliation (read-only)

**Status: independent QA candidate; not deployed, not a live website test.**

## Narrow, newly verified evidence discrepancy (October 29–30, 2026)

The WordPress media API currently reports **media ID 1737**:

- Public asset: \`/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf\`
- MIME: \`application/pdf\`; size: **599,946 bytes**
- The media **description field** manually reports SHA-256:
  \`8d1a0153f54ce10adf0b1a268a7f3d2d6d636dd87058511ba59e5a404064f8f4\`

Separately, an earlier QA examination of a **local** candidate named \`Final_Vestige_Seven_Day_Focus_Fieldbook_Launch.pdf\` reported **52 readable pages**, **599,946 bytes**, and SHA-256:

\`84af8dc1e4231de9aea383ad6bc4dfa3251cfb2440f0ab3a755769bd7c28d3fb\`

That earlier examination is documented in [issue #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129#issuecomment-6514574209). These two **reported hashes differ despite identical reported byte lengths**. They may describe *different builds of the PDF*, or the manually entered media description may be stale. **No currently available evidence establishes the hosted file's actual SHA-256.** This is an evidence-attribution mismatch, **NOT** proof of an altered, invalid, malicious, or inaccessible public download.

Public GET of the PDF and website is inaccessible from the current isolated QA container (DNS lookup of even unrelated external domains fails). The WordPress connector reports metadata but not the hosted asset bytes. Therefore neither the current metadata SHA nor the earlier local SHA is proven to be the hosted checksum.

## New QA capability

\`focus_pdf_digest_guard.py\` is an **offline-only**, read-only, pure-Python checker for a sanitized media.get response. It can independently compare a separately observed SHA-256 claim or calculate a local candidate PDF SHA-256. It:

- Strictly binds evidence to media ID 1737, the expected first-party HTTPS host, PDF filename, MIME and bounded size.
- Rejects ambiguous/conflicting metadata digests and malformed comparison hashes.
- Checks local candidate PDF magic and EOF, size and digest with a 16 MiB input limit.
- Explicitly outputs \`hosted_pdf_verified: false\` for **every** possible state. Local agreement or disagreement **never** certifies an online asset.
- Creates no subscribers, pages, network calls, credentials, routes or WordPress changes. It does not contact, modify, nor compete with Claude's active WordPress editing.

Quick local check (save a sanitized WordPress \`media.get\` response to \`/tmp/media.json\` first):

\`\`\`bash
python3 qa/integrity/focus_pdf_digest_guard.py \
  --media-json /tmp/media.json \
  --independent-sha256 84af8dc1e4231de9aea383ad6bc4dfa3251cfb2440f0ab3a755769bd7c28d3fb

python3 -m unittest discover -s qa/integrity -p 'test_*.py' -v
\`\`\`

A replay of the exact published WordPress media metadata and earlier independently reported digest returns \`CONFLICTING_DIGEST_CLAIMS\`, exit code **1**; this is **REVIEW**, not public PDF failure.

## Required to resolve, in priority order

1. On a network-capable host, download the **actual first-party asset** from the complete WordPress media URL. Confirm an HTTP 200, HTTPS final destination, correct content type, PDF magic/EOF and actual bytes; the public GET checks are **already implemented separately in draft PR #133**. Avoid duplicate public-fetch code here.
2. Compute **SHA-256 from those downloaded bytes**, not from a file with a similar name. Run a PDF parser to verify 52 pages, and inspect a couple rendered pages to confirm it is the current Complete Edition.
3. Compare downloaded SHA against both values above. If the published file matches the media description, the local candidate is merely different. If the published file matches the local digest, the stored description is outdated. If neither, investigate artifact build provenance/expected publication release. **Do not assume either value is authoritative.**
4. Only after determining ground truth, use the established Claude/editor approval/QD process to update **only** any stale media description or replace a faulty PDF if necessary. Preserve legacy links, the live welcome-email link, existing opt-ins and any earlier purchasers' rights. Never silently replace the live media from this QA lane.
5. Confirm anonymous mobile browser form→confirmation→welcome→PDF link delivery separately. The founder previously reported actually receiving a welcome email, but this run did not repeat that test.

## Verification and release boundaries

18/18 **native local Python unittest** checks pass; \`py_compile\` passes. Commits were checked by comparing the resulting GitHub blob SHA-1s to local \`git hash-object\` results:
- Guard: \`1a87b2c003bfabf4c95bd9b10144d2e3a81d6b29\`
- Tests: \`20c8bef1bf23f294331b299aefcc9b437ab04090\`

No PR merge, WordPress write, plugin change, redirects, uptime-monitor activation, subscriber import, production deployment, or added cost is authorized. The earlier draft PR #133 continues to own public HTTP/PDF byte-smoke checks; this PR adds only **checksum claim attribution and offline candidate comparison**.
