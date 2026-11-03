# PR #604 exact-block render on WordPress.com (private draft 1902), 2026-11-02

Gate 2 of `PR604_GATE_PACKET.md`. Performed in the in-app browser, signed in to WordPress.com by the founder (no credentials entered by the assistant). **Draft only: nothing was published and live page 6 was not touched.**

**Subject:** PR #604 head `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`; block `replacement-block-index1.html`, 108,155 bytes, SHA-256 `506aa8d9d9d9c3fe7821d8e479dc8857957667f06f5f6ea5432e3f3ad0fbc7c9`, SHA-1 `8c0dd5c3adce073fd58f5001e0f90d523ffad277`. The block was extracted from that git commit and verified against all three values before use.

## Result

**PASS for the draft render, with the limits listed below.** This closes the matrix's B5, and the parts of B6 that a single-block draft can show. It does not by itself release anything.

| Check | Result | Evidence |
|---|---|---|
| Exact block stored unstripped (B5) | **PASS** | REST `content.raw` equals the file byte for byte (108,155 bytes); `page-sections.list` reports `block_hash` and `content_hash` both `8c0dd5c3adce073fd58f5001e0f90d523ffad277`; the editor parses it as one valid `core/html` block with no inner blocks |
| Draft stays private | **PASS** | `status: draft` after every save; preview opened only via the signed-in session |
| Live page 6 untouched | **PASS** | read before and after: `modified 2026-10-30T09:14:14`, `content_hash 7afdb933d2ec68fd993ef015c97a6eb9edfe0576`, block hashes for indexes 0 to 5 identical |
| Renders inside Assembler | **PASS** | site header and footer present, one `main`, one `h1` ("Find what others miss."), flagship root present, 357 KB of HTML served, inline `<style>` and `<script>` intact |
| Seven chapters and chapter bar | **PASS** | seven links: 01 The find to 07 The observer |
| Anchors | **PASS (after correcting my own method)** | all seven land at 130 to 138 px with the sticky nav ending at 66 px. A first pass reported four "not clear" because it measured before smooth scrolling had settled; the settled re-test is the result |
| Case chooser | **PASS** | three cases; `aria-pressed` follows clicks; only the chosen panel visible; status text updates ("Now viewing: ...") |
| Archival images | **PASS** | each loads once its case is selected: Apollo 516x401, Franklin note 515x820, Malbone map 516x348 (via the Jetpack CDN). Images in unselected panels are lazy and do not load until shown; this is by design |
| Franklin document switch | **PASS** | Original, Addition, Compare both; pressed state follows |
| Observer Lab | **PASS** | Frame A and Frame B toggle with correct pressed states |
| Disclosure (`details`) | **PASS** | 8 present; toggles |
| Skip link fix (WCAG 2.4.11) | **PASS** | with genuine focus and `:focus-visible`: `position:fixed`, `z-index:100001`, transform none, box 9,9 218x45, and the top-most element at all three sample points. Screenshot confirms the label is fully legible above the header |
| Horizontal overflow | **PASS** | none at 320, 390, 768, 1440, 1920 |
| Console | **PASS for the flagship** | 29 error messages, all WordPress.com or Jetpack noise from the logged-in view (duplicate store registrations, a blocked tracker, "jetpack-connection already registered"); a search for flagship, `fv-hf`, `Uncaught`, `TypeError`, `ReferenceError`, `SyntaxError` found nothing |
| Network | **PASS** | every first-party request in the sampled window returned 200 |

## What went wrong on the way, and the lesson for the operator

The first save put **two nested `<!-- wp:html -->` wrappers** into the draft: the block file is already the full serialized block, and I inserted it as the *content* of another HTML block through the editor. WordPress.com's own listing exposed it immediately (`block_hash 93e86f57...`, `has_inner_blocks: true`, empty preview), which is the reason this gate exists. I corrected it by writing the file's text as the page content through the REST API and re-verified the hash. **For the real release, `page-sections.replace` takes `block_markup_file` as the complete block markup exactly as committed; do not wrap it again.** Check `block_hash` equals `8c0dd5c3...` after the write.

## Limits (not covered by this render)

- The draft contains only the flagship block. It does **not** exercise the preserved blocks (Margins strip, Focus CTA, Jetpack Dispatch, Enter the record, JSON-LD) or the interplay with them; that composition was tested only on the local WordPress stage and will be verified on the live page after the write.
- Measured with the in-app browser's own tools, not the repository's Playwright suite: no axe run and no Lighthouse on WordPress.com in this session (a private draft needs the signed-in session). Earlier axe results are from the local stage.
- The preview is a logged-in view (admin bar); real-visitor timing and Core Web Vitals on WordPress.com are not measured.
- No screen reader, Safari, iOS or real-device test. JavaScript-disabled behaviour on WordPress.com was not tested here (local stage only).
- Draft 1902 was left in place (private, unpublished, titled "delete after verification") so it can be inspected again; it should be trashed after the release.

## Still open before go-live

Fresh independent review of `bdf01b4a3e`, and the named-editor NASA sign-off. Gate 4 (LCP exception) is approved.
