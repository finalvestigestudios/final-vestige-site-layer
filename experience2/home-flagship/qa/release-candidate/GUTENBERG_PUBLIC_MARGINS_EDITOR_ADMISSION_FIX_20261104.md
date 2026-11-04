# EX2 P0: unblock actual Gutenberg / Assembler admission — public Margins manifest custody

**Status: DRAFT / RELEASE HOLD.** Based on exact parent PR #960 HEAD `e5515f8ed21b49fca472538ff921330c89b30541`. Do not modify, merge, deploy or publish PR #49 or live WordPress page 6.

## Concrete blocker found by reading producer and actual runner

The seven-chapter candidate producer `write_source_flagship_playground_candidate.py::compose()` emits:

```
data_classification = PUBLIC_PAGE6_MARGINS_WITH_SYNTHETIC_JETPACK_FIXTURE
public_page6_margins_texts_included = true
page6_live_content_included = false
other_page6_content_included = false
```

Before this PR, `playground_gutenberg_editor_gate.mjs::checkManifest()` **unconditionally demanded** `SYNTHETIC_TEST_FIXTURE_ONLY`. Its PHP editor receipt and `checkEditorReceipt()` also used the obsolete synthetic-only data class. Therefore the source-controlled full candidate failed **before loading WordPress Playground, Gutenberg, Chromium, axe or Assembler** even if GitHub Actions runners began executing. This is not a hypothetical or a hosted-site observation: it follows directly from incompatible exact-source equality checks.

The fixture is a 72-record *public* WordPress page-6 Margins snapshot, with a synthetic Jetpack stub. The `SYNTHETIC_TEST_FIXTURE_ONLY` **environment marker remains** mandatory for the disposable loopback site. The marker is NOT a statement that the 72 published records are invented.

## Fixed with fail-closed provenance validation

- The editor runner now accepts only the producer's one exact **public-Margins + synthetic-Jetpack** classification. It additionally validates release HOLD, public-only source boundaries, all 11 source-file fingerprints and seven chapter IDs, candidate hash/byte length, and CSS/JS/Gutenberg invariants.
- The editor verifies the checked-in JSON source fixture's SHA-256, site ID **256784396**, page ID **6**, source URL, revision timestamp and **all 72 individual published text nodes in order** against the candidate's serialized HTML. It does not fetch or copy the live WordPress database or subscribers.
- PHP create/verify receipts correctly report the public-Margins classification. Server-side loopback, fresh token, synthetic-environment marker, draft-only status, HMAC ownership, exact stored-content hash and verified deletion are preserved.
- The existing checked-in Python source test now contains a producer/JS/PHP cross-contract regression, and the existing Node `--self-test` now has a positive fixture-backed case and adversarial data-class, provenance, candidate hash, source inventory and receipt mutations.
- No change to the eleven flagship source files, seven chapters, archival media, CTA, theme, public CMS, payment tracking, affiliate links or acquisition workflow.

## Evidence / exact release admission

1. Verify branch SHA and manifest: `git rev-parse HEAD`, then `python -I -m unittest discover -s experience2/home-flagship/qa/release-candidate -p test_source_flagship_playground_candidate.py -v`.
2. Execute `node --check experience2/home-flagship/qa/release-candidate/playground_gutenberg_editor_gate.mjs`, then `node experience2/home-flagship/qa/release-candidate/playground_gutenberg_editor_gate.mjs --self-test`, and `php -l experience2/home-flagship/qa/release-candidate/playground_gutenberg_editor_gate.php`.
3. Assemble the real 11-source candidate into **unused private local temporary paths** using `write_source_flagship_playground_candidate.py --output ... --manifest ...`. Reject discrepancies in manifest/public source.
4. Only in disposable loopback WordPress Playground with free Assembler, perform the EXISTING real Gutenberg editor Save/readback and anonymous five-width WordPress front-end gate (whole-document axe, images, keyboard/no-JS, physical CTA, cleanup). This PR does not perform any CMS write.
5. Retain **HOLD** on any CI failure, axe violation, missing image/rights, anonymous failure, no-JS failure, hosted parity gap, physical zoom, independent QD or founder visual approval. WordPress Playground is NOT WordPress.com Atomic or Jetpack hosting parity.

**CI evidence as of 2026-11-04:** parent SHA `e5515f8...` workflow 41864218683 and CI 41864218878 were marked completed/failure with zero job steps reported; GitHub job log fetch for both returned `BlobNotFound`. Root cause of runner dispatch is **not established**. Source-contract fix is not CI-green or WordPress-certified without execution.

## Conversion decision

**OFFER →** existing 52-page Seven Day Focus Fieldbook (no unverified Inspire3 offer).

**FUNNEL STEP →** evidence-first, anonymous homepage visitor → unobstructed contextual Focus action → independently confirmed lead (if observable).

**BLOCKER →** exact-source staging never started because the editor's provenance contract rejected the builder's real public data.

**CHANGE/EXPERIMENT →** admit only the correct cryptographically linked public fixture, run the existing isolated Gutenberg + anonymous browser release matrix, do not add paid scripts.

**PASS/FAIL EVIDENCE →** source-level contradiction closed; real end-to-end WordPress, CI, axe and performance remain **PENDING**, paid conversions **UNKNOWN**.

**OWNERS →** homepage engineering: this QA repair; Claude: revenue/attribution; Grok: social assets; Praxxis: independent QA; founder: production releases and spending.

No production publishing, plugin installation, email, tracking writes, merge, deployment or new cost. The frozen v1 PR #49 remains untouched.