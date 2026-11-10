# R245 supplementary audit — never send

Run with Node 22: `node --test dispatch/r245/tests/temporal_truth.test.cjs`.

The exact GitHub blobs for the new implementation and tests have been checked against the local code that passed all 24 native tests. The original campaign's native Python tests independently pass 6/6 from the authenticated original source archive.

**Do not** merge this reviewer into commerce code or interpret its outputs as real purchases. Its only business outputs are **NULL** for verified paid orders and net revenue. It evaluates civil-time integrity, report cutoffs, duplicate opaque IDs, and basic causal chronology of synthetic or properly redacted ledger records, *in addition to* R244; it never authenticates external partner receipts, list consent, or legally compliant emails.

See [the evidence and conversion plan](./EVIDENCE_AND_CONVERSION_RELEASE.md) and [machine-readable release truth](./RELEASE_TRUTH.json). Source of truth: Issue #174, companion #171, original PR #175, readiness PR #201, stacked parent R244 #1818. The founder has **not** approved sending.

**No production side effects:** the source imports no network clients and has no writing operations. All six editions HOLD_UNSENT; affiliate #03/#05 HOLD_MERCHANT. WordPress/email delivery and opt-out need separately authorized observation; the original subscriber list is not exported. Homepage PR #49 stays untouched.
