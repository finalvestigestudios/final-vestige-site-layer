# GrantAudit Studio Pro — linked reimbursements R6

**Pre-release; synthetic test data only.** This is an offline, deterministic financial review aid, not an audit opinion, eligibility finding, payment authorization or fraud determination. All source documents remain local. Windows binary verification, premium entitlements, malware screening and QD review are outstanding.

## Modes and input contracts

**Legacy:** Claims use id, amount, program. Ledgers use the same identifier and program. Existing matching and three-file output contracts remain unchanged. The presence of claim_type or related_claim columns **without ledger_reference** is now a fail-closed error so reversals cannot silently be counted as positive claims.

**Linked:** Claims CSV contains claim_id, amount, program, ledger_reference, plus optional claim_type and related_claim. The required ledger_reference points to a ledger transaction_id, even when the claim identifier or program differs. Ledger rows must include transaction_id, amount, program; budget rows include program, budget. All claims in linked mode require an explicit source reference; no automatic key guessing. The presence of ledger_reference in the header enables linked mode, even on an empty claims file.

**Credit memos:** Linked claim_type is claim (default) or credit; credit amounts are positive and must include a related_claim identifier pointing to an original claim within the same ledger transaction. Negative claim inputs are rejected. Reversals, zero claim amounts, cross-program credits, repeated claim identifiers, punctuation-normalized links, and over-credits get visible human-review flags.

## Worked synthetic example

See examples/grants-r6/{claims,ledger,budgets}.csv.

- LEDGER-100 is allocated $60 to PROGRAM-A and $40 to PROGRAM-B. The ledger records $100. Despite exact arithmetic, the report flags split_allocation_review and ledger_program_context_review.
- LEDGER-200 has a $10 claim and an explicitly linked $2 credit to that claim. Net $8 reconciles to the ledger but retains credit_memo_review.
- PROGRAM-A budget usage is $60 + $10 - $2 = **$68**; PROGRAM-B usage is **$40**. Both budgets still require source documentation review.
- Three outputs are generated: a source-linked exception report, program budget report, and SHA-256 byte-inventory manifest. Original input CSVs are never overwritten.

The exception report appends gross amount, credit amount, net amount, allocation source-row lineage and original identifiers. The first 12 legacy columns, and the first five budget columns, remain in place. Financial totals use Decimal. Budget totals are program-based; ledger reconciliation sums by explicit source transaction ID. Lossy normalized ID/program collisions are shown for review, not treated as definitive source identity.

## What this does NOT do

This tool does not evaluate grant award terms, allowability/eligibility, claim timing, procurement rules, cash-versus-accrual, indirect cost rates, match rules, tax, currency conversion, sanctions, evidence sufficiency or record retention. It does not provide encrypted-at-rest storage, reviewer approvals, digital signing, or multi-user case management. Human review is always required; a matched flag confirms arithmetic only. Do not use pre-release tools with protected production financial documents.

## Validation / release controls

An isolated Python 3.13.5 harness exercised the candidate linked-allocation code against compatible CSV parser, export and Decimal helpers: **21 local integration tests passed**. This branch adds **24 repository tests** covering linked and legacy routing, but the complete repository suite and all six packaged Windows binaries remain **unverified** because hosted Actions jobs have been failing before any runner steps start. Passing the isolated harness is not equivalent to a verified Windows release.

Once runners recover, run from the repository root:

    PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v

Then run the six packaged executables with --smoke-test, verify checksum contents, test on a clean Windows 11 VM, perform AV/security and keyboard accessibility checks, implement paid entitlements, and submit source + built artifacts for QD review. No public download links until those gates pass.
