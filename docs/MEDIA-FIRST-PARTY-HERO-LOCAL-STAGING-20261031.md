# Local first-party hero derivatives — guarded five-image staging (2026-10-31)

**Draft PR #183 only.** This is a practical follow-on to the source-to-Jetpack reconciliation, **not** a public-site repair or a claim about what browsers downloaded. Site QA PR #154, homepage design, WordPress content and published media are untouched.

## Exact five-item scope

The authenticated, read-only WordPress source/media review associated the following first-party original PNG images with both featured and inline placements. All are **1672×941** pixels, have **no registered WordPress sub-sizes**, and have a **proposed 960×540 WebP derivative**, without upscaling:

| Media ID / post | Original basename | Original WordPress storage bytes |
| --- | --- | ---: |
| 39 / 34 | bceca0bd-a16f-44f7-be08-16376fbf08ca.png | 2,892,087 |
| 40 / 35 | 377e08da-e121-4f57-9174-1548343402b3.png | 2,552,136 |
| 41 / 36 | a44f673d-a8a8-4c83-9f29-7e24dd55156b.png | 2,498,247 |
| 42 / 37 | c1237ffd-4a47-4988-8254-e3b021069e72.png | 2,488,823 |
| 43 / 38 | 01340c2e-1165-4ca0-aa96-87398a83d13a.png | 2,836,245 |

Combined original **storage**: **13,267,538 bytes**. The above is not a five-post browser waterfall or an assertion that customers receive these original bytes. Cross-check: \`qa/media-recovery/oversize_inline_reconciled_20261031.json\`.

## Runnable offline deliverable

- \`qa/media-recovery/prepare_hero_derivatives.py\`: local-only Python 3/Pillow candidate encoder (quality 90 WebP) with strict five-media-ID whitelist; exact source filename, 1672×941, byte count, original SHA-256 and manually reviewed rights/identity gates; no-upscale, no overwrite, original files unchanged, output in a **separate local staging directory**, locally measured sizes/hashes and machine-readable evidence. There are **no network calls, WordPress API calls, uploads, or post edits**.
- \`qa/media-recovery/test_prepare_hero_derivatives.py\`: 13 native Python tests, using synthetic test art exclusively, including actual local PNG-to-WebP encoding; malformed hashes/rights/source URLs, missing visual review, wrong dimensions, symlinks, unknown media IDs, missing approvals and overwrite rejection.

**Verified locally:** \`python -m unittest -v test_prepare_hero_derivatives.py\` → **13 passed, 0 failed** (Python/Pillow local runtime, 2026-10-31). The two exact committed Git blob SHA-1s match the locally tested files: encoder \`20abbb8928a349f6e0418772695bbe2c00faf2ce\`; tests \`840d722828e5a7b424695e2b53471bd3aa699e21\`. Native GitHub CI and public browser validation were **not** performed.

### Safe usage, if legitimate local masters become available

\`\`\`sh
python qa/media-recovery/prepare_hero_derivatives.py --plan
python -m unittest -v qa/media-recovery/test_prepare_hero_derivatives.py
python qa/media-recovery/prepare_hero_derivatives.py \
  --media-id 39 \
  --input-dir /path/to/legitimately-held-originals \
  --output-dir /separate/local/review-staging \
  --approvals /path/to/individually-reviewed-approvals.json
\`\`\`

Approval JSON must be \`{"schema_version":1,"items":[{"media_id":39,"source_url":"https://finalvestige.com/wp-content/uploads/2026/08/bceca0bd-a16f-44f7-be08-16376fbf08ca.png","original_sha256":"<64-character SHA256 of actual local original>","rights_basis":"original_work_owned","rights_evidence":"<substantive item-specific evidence>","credit_text":"<required creator credit>","reviewer":"<reviewer's name>","reviewed_on":"2026-10-31","visual_identity_reviewed":true,"no_wordpress_write":true}]}\`. Sample is **illustrative, not an approval**; actual rights/ownership remain unverified. Approvals are self-attestation gates, not independent legal determinations.

The local encoded-size reduction, if achieved, **must not** be reported as the original **76% page-weight reduction**. Compare original and WebP visually (especially line/text legibility, color, transparent edges and reconstruction notices); confirm preserved attribution; manually inspect browser currentSrc, responsive behavior and image-transfer bytes after any separately approved future CMS staging. Review WordPress media placement and post-caption changes individually; do not automate block rewrites.

## Material limitations and next action

No original binary was obtained or converted in this sprint. Only synthetic images were processed in native tests; output bytes and hashes of actual Five Heroes remain **unknown**. Production broken-image count (**42**) and claimed **76%** weight saving are unverified. This code enables real authorized asset preparation as soon as legitimately obtained image masters, item-level rights review, and browser evidence are available.

**Priority:** 1. Logged-out browser proofs for the 36 P0 offsite image slots and actual failures; 2. first-party five-hero transfer measurement; 3. only then rights-approved local derivatives and controlled editorial/WordPress review. Never automatically download unlicensed archives or mirror external URLs.
