# R96 — ProcureGuard source document lists are display-only, unambiguous evidence

Status: draft source implementation. **No payment/compliance determination,
native Windows acceptance, executable release, or website publication is authorized.**

## Defect and predecessor

The R95 ProcureGuard review_line response formats three older human document-list
fields — invoice_documents, credit_references and return_references — with raw
Unicode. A bidirectional override, blank filler, carriage return or invisible
space can make source references misleading to a human reviewer. The newer
receipt_documents and return_documents fields already used visible_source_text,
but none of these five fields escaped literal semicolons, allowing a source label
to look like multiple joined documents. This is a **presentation** ambiguity,
not a matching error or proof of fraud.

## Implementation

Use a single pure offline audit_display.visible_source_label_list for all five
fields. It deduplicates and sorts raw source labels deterministically, trims
only ordinary outer ASCII spaces (preserving hidden Unicode evidence), then
escapes controls, bidirectional/blank Unicode and literal backslashes through
visible_source_text. Source semicolons become literal backslash-u-003B while
actual list separators remain semicolon plus space. Typed source text that
resembles an escape sequence keeps its own escaped backslash and therefore
remains distinct from the rendered hidden character.

This code changes only human-facing display values: source CSV snapshots,
SHA-256 fingerprints, physical row citations, matching keys, Decimal
calculations, decision flags and journal history are unchanged. Never use
display strings to reconstruct source bytes; consult original verified inputs.
No output automatically decides eligibility, fraud, policy or payment.

## Verification boundaries

- Local Linux Python 3.13.5, actual modified audit_display module with the
  exact GitHub blob, plus unchanged exact-blob unicode_hazards dependency:
  **18/18 focused unittest methods pass**, normal and optimized -OO.
  Includes 200,000 distinct synthetic references and hostile Unicode.
- Additional **five committed repository integration methods are unexecuted**
  in the isolated workspace. Their Python source compiles; they cover all five
  output fields, actual local CSV-to-manifest flow, source-byte preservation,
  literal-source escape distinction, immutable inputs and unchanged money flags.
- The complete repository, all six native Windows 11 x64 GUIs/EXEs, malware
  scanning, signing/checksums, premium entitlement/download protection,
  accessibility and independent QD/founder approval remain **unverified**.
  No executable or premium download may be distributed.

## Next decisive action

Resolve GitHub Actions runner initialization issue #75, prove one real source
step executes, then run all 23 R96 repository tests and the complete desktop
suite in normal and -OO modes. Continue with Windows x64 six-program smoke,
AV/keyboard/checksum/access-gate verification and independent QD approval.
Do not merge to production or publish release assets before those gates pass.
