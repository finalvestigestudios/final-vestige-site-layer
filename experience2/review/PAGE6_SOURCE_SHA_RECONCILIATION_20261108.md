# Page 6 SHA-256 custody reconciliation — 2026-11-08 UTC

**Status: source pin corrected; REVIEW ONLY; RELEASE HOLD.** No CMS writes, merge, production install or tracking changes.

## Blocking regression found

Draft PR #1548 (`cfcfd7fe0bf7ab931ac3a1a9b3f2b30d3a628823`) pinned raw WordPress Page 6 content to `685911178ae68ca9dfbd8f47f5903ef57f76ac4b52e886d8287416304c98794b`. Its PR explicitly noted that the original hash was **not recomputed** from a fresh full authenticated page export. Fresh `wpcom_mcp_pages_get` using **context=edit** and the literal `content` string instead yields:

- Authenticated site: `finalvestige.com`, WordPress page ID **6**, `publish`.
- Page modified: `2026-11-05T12:07:24` (reported by WordPress).
- Raw Gutenberg/content string length: **150,710 JavaScript UTF-16 code units**.
- **Fresh SHA-256 of UTF-8 content:** `1188d32a101896f12af9823dd7ca4b8a12b0c36684e82c069f23855a698e5669`.
- Focus landing page ID **1579**, publish, modified `2026-11-05T17:44:02`, raw content 31,876 UTF-16 code units.
- Crypto implementation verified against SHA-256 of empty input, `abc` and UTF-8 emoji `😊`; the latter matches Python's `hashlib.sha256('😊'.encode())`.

The original `assemble(home, focus, {hashFn:()=>actual_sha})` **correctly FAILED** with `HOLD: exact homepage SHA mismatch`. This means the `node --home ... --focus ...` CLI from #1548 would have held on the current authenticated source despite all 17 earlier synthetic tests passing.

## Scoped fix and verification

This stacked branch corrects **only the source pin** in `atomic_page6_review.cjs`, adds a source-custody annotation, and adds two native non-injected SHA tests. Its Page 6 replacement instructions are unchanged.

The exact GitHub #1548 module with `PIN` replaced to the new digest was evaluated *directly against fresh authenticated Page 6 and Focus page raw content in V8* (Node module wrapper only; crypto digest was independently computed). It completed all five atomic substitutions and byte-for-byte reversal. Before/after invariants:

| Preservation | Before | Proposed |
|---|---:|---:|
| Chapter destination IDs | 7 | 7 |
| Hidden in the Margins | 72 | 72 |
| Image elements | 4 | 4 |
| Jetpack subscriptions block | 1 | 1 |
| Contextual Focus destinations | 4 | 5 |
| Scripts / styles / Gutenberg blocks | 5 / 4 / 112 | 5 / 4 / 112 |
| Apollo / Franklin / NYPL media references | Preserved | Preserved |

**Five reversible substitutions**: secondary hero to Focus, Dispatch cadence to publication-dependent wording, adjacent commission/privacy disclosure, readable inline 14px font, matching Gutenberg block font metadata. A candidate was created **in memory only**, not installed/published/written to the CMS. The old source pin remains in Git history for independent review.

## What this does NOT establish

No native WordPress/Assembler staging execution, no real Jetpack subscriber proof, no real archival-media byte transfer, no independent axe/WCAG 2.2 AA, no Lighthouse/CWV metrics, no CI/QD approval or paid conversion. NYPL map exact-item rights remain unresolved. The source may change again; rerun against a fresh `context=edit` export **before any release decision**. The WordPress.com Personal plan does not provide a native staging clone. Prefer isolated WordPress Playground or local WP developer instance and retain separate hosted acceptance requirements.

## Reproducible verification

Export only public Page 6 and public Focus Page 1579 as local JSON objects with `id`, `status`, `modified`, and raw `content`, using authenticated `context=edit`. Never include subscribers, cookies, credentials, private drafts, or production DB exports.

```sh
node --test experience2/review/test_atomic_page6_review.cjs
node experience2/review/atomic_page6_review.cjs --home home-edit.json --focus focus-edit.json --out fresh-review.html
```

The CLI refuses to overwrite source/output files, creates local-only 0600 review artifacts and returns `release: HOLD`. The actual new PIN is source-specific, not a CI/production approval.

**Conversion contract:** Focus Fieldbook → eligible reader → actual Jetpack confirmed subscriber → independently confirmed purchase/affiliate conversion → fees/refunds → realized net revenue. The corrected proposal has **no measured paid-conversion effect**.
