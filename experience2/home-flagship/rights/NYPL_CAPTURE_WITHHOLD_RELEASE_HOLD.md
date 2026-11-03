# EX2 — Malbone / NYPL digital capture — rights-safe offline release candidate

**Status:** DRAFT / RIGHTS HOLD / NOT PUBLISHED.  
**Owner:** Homepage engineering; independent art/editorial/legal rights and QD reviewers required.  
**Source read:** WordPress.com production **page ID 6**, site **256784396**, status \`publish\`; reported modification \`2026-11-02T17:48:13\`.  
**Source:** Gutenberg raw content, read in-memory with the connected WordPress MCP tool on 2026-11-03. **No production mutation.**  
**Target:** NYPL digital capture referenced by homepage Malbone evidence case; catalog item **5003296**, item record \`c745e730-d2a9-012f-5ecc-58d385a7bbd0\`.  
**Source record:** https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0  
**Institutional reuse policy:** https://digitalcollections.nypl.org/about

## Exact actual production issue

Published page 6 embeds the file \`edit-017-v02-nypl-5003296-original.jpg\`
in one \`<img>\` with \`src\` plus responsive \`srcset\` candidates; the filename appears
four times in the raw source. Nearby prose asserts that NYPL believes the
specific image is public domain under US law. The available institution-wide
policy does **not** substantiate this capture-level statement. This is a
*missing documented rights decision*, **not** a finding of infringement.

Actual readback simultaneously located:
- 72 individual \`style="--i:N"\` Margins entries (0..71);
- one Jetpack subscriptions Gutenberg block;
- five textual \`Fieldbook\` occurrences;
- four original \`data-fv-archive-img\` references, including the one NYPL image;
- linked NYPL catalog source references and the Malbone chronology.

The image's source credit and catalog link are useful and should remain even
when displaying its digital reproduction is withheld.

## Scope of this PR

\`withhold_unverified_nypl_capture.py\` creates a **separate offline
candidate raw page-6 markup file** from a locally held, independently
SHA-256-verified export. It never reaches WordPress or writes back to its input.

The transformer:
1. Looks for exactly one matching Malbone evidence case and exact NYPL binary
   \`<img>\` carrying source and srcset; fails closed on any unreviewed binary.
2. Removes that one image tag. The **existing styled text fallback** (1903,
   NYPL Digital Collections, and the link below) becomes visible. This
   preserves the editorial image-frame composition without pretending the
   underlying visual is a reproduced map.
3. Rewrites the inaccurate public-domain certainty into a clearly
   **unverified-rights** statement, updates the image caption to a linked
   catalog-record caption, and relabels a decorative archival frame.
4. Asserts the 72 margins, Jetpack block, Focus, source links, remaining
   archival images, Gutenberg markup, Franklin/Apollo cases are preserved.
5. Emits a JSON artifact manifest with before/after source SHA-256 and
   inventory, **not source content**, for reviewer attestation.

### Manual invocation — only after independently obtaining allowed PUBLIC page-6 raw HTML

\`\`\`bash
python - <<'PY'
from hashlib import sha256
from pathlib import Path
print(sha256(Path("home-page-6-raw.blocks.html").read_bytes()).hexdigest())
PY
python experience2/home-flagship/rights/withhold_unverified_nypl_capture.py \
  --source home-page-6-raw.blocks.html \
  --output homepage-page-6-nypl-held.blocks.html \
  --report NYPL_RIGHTS_REVIEW.json \
  --expected-sha256 <independently-verified-64-char-sha256>
\`\`\`

Do **not** commit raw WordPress exports or any subscriber/account/secret data
to the repository. Export only publicly published page-6 markup, if permitted.
Avoid database WXR or staging sync. Always re-read site page ID, \`modified\`,
and hashes before proposing an eventual gated release.

## Explicit acceptance limits

This PR **does not** modify page 6, any theme/CSS, any plugin, or any remote
media file. No WordPress secret, production WP REST key or application password
is used. No hosted-page comparison or visual screenshot is claimed for the
offline candidate. Existing tests are *synthetic source contract* tests; the
specific live source was independently inspected with read-only WordPress
tooling, but the patch has **not** been exported and executed on a full 150 kB
live raw page through GitHub CI.

Release remains HOLD pending original item **capture-level rights** review,
exact-source WordPress/Assembler test, art-direction review of the styled
fallback, independent QD, hosted accessibility and performance checks,
provenance/disclosure review, and express founder approval. A WordPress.com
Personal plan does not include native staging; use separate free isolated
WordPress Playground for a safe preview and retain hosted acceptance separately.

Frozen #49 is unchanged. This is a companion to #772, not a replacement for
the seven-chapter flagship, Focus Fieldbook or original 72 Margins records.
