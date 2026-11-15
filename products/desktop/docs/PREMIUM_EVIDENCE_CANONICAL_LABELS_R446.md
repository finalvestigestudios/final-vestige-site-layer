# R446 — deterministic, reviewer-safe premium evidence labels (DRAFT / RELEASE HOLD)

Issue [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). This is a **stacked draft** based on R445; production `main` is unchanged.

## What was fixed

The premium inventory reader previously accepted alternative escaped JSON spellings for a basename, for example `\\u0069nput-0.csv` as an alias of `input-0.csv`. It also accepted decoded tab/control, bidi override, zero-width, surrogate, and noncharacter labels for *source* rows, even though those labels can deceive a reviewer of an audit inventory. Report hashes and file bytes still had to match; this was a **label-integrity / human-readability** issue, not demonstrated bypass of SHA-256.

R446 introduces one shared formatter used by both the local writer and post-publication verifier. Before any input/report file hashing, the writer checks basenames. The verifier decodes each source/report label, validates it, and requires **exactly the canonical ASCII JSON escaping emitted by the writer**. It rejects Cc/Cf/Cs control, formatting and surrogate characters; Zl/Zp separators; non-ASCII whitespace except ordinary ASCII space; and Unicode noncharacters. Visible international text, including accented letters and CJK, still works. Existing NFKC/casefold duplicate detection stays in force. File contents, original records, money calculations, SHA-256 semantics, report provenance and review decisions are unchanged.

This validation is deliberately strict: a rare legitimate original file whose name contains invisible characters may be rejected. The **human-reviewed remedy** is to rename a copy of that source, rerun reconciliation, reissue the inventory, and retain the original unchanged. Do not automatically rewrite or silently normalize names. A previously exported inventory with noncanonical or invisible labels is held for review, not automatically trusted.

## Artifacts

- `products/desktop/fvs_suite/evidence_label.py` — canonical printable basename formatter
- `products/desktop/fvs_suite/manifest_guard.py` — check names before opening private source/report evidence; write canonical labels
- `products/desktop/fvs_suite/premium_manifest_completion.py` — fail closed on noncanonical or misleading decoded labels
- `products/desktop/tests/test_evidence_labels_r446.py` — 13 synthetic regression methods covering both premium app package shapes, Unicode, writer early refusals, escaped aliases, unchanged report bytes and tamper detection
- `.github/workflows/desktop-source-evidence-r385.yml` — both-OS normal and `-OO -W error` R446 plus inherited R254/R255 manifest cases

## Test evidence and strict limits

Executed locally on Linux with a **reconstructed premium writer/verifier projection**, a copy of the new helper, synthetic real temporary files, and local implementations of the three descriptor/hash dependencies. **13/13 standard PASS; 13/13 optimized PASS; Python compileall PASS**. The focused projection exercised real local hashes, read-only verifier checks and three package layouts. **Not** a full checkout, actual GitHub-blob parity claim, Windows test, or an assertion that all committed R446 tests ran in a GitHub runner. Inherited suites and the complete six-engine financial suite await actual source CI. Prior R445 workflows failed with zero recorded steps; hosted-runner root cause unconfirmed.

## QD and release custody

**HARD HOLD: release_authorized=false.** These are local-first report checks, not compliance certification or payment approval. No source upload, telemetry, financial authorization, license, Windows EXE, premium artifact, download URL, WordPress deployment or direct production branch change. Independent QD review and explicit founder approval must precede any release.

Next: restore hosted-runner availability (inspect workflow failure annotations, Actions billing/limits and repository policy), run exact-head R446 source + inherited tests on Ubuntu and Windows, six-engine financial regressions, real Windows x64 packaging/smokes/Defender/SHA-256, and verify premium access-controlled delivery before QD/founder review.
