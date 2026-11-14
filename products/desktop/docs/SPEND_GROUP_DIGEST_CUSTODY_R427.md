# R427 — SpendMap vendor/month fingerprint input custody

**Issue:** #73. **Status:** SOURCE ONLY; NO BINARY RELEASE. **Parent:** R426 draft #2475; not production `main`.

## Problem and scope

R426 required a native, lowercase SHA-256 for the source snapshot, but the
separately callable `_vendor_month_line_digest` still accepted a `str`
subclass for its vendor/month identity and arbitrary source-row sequences.
A direct caller could override `.encode()` to hash bytes inconsistent with
the displayed group identity, or supply duplicate/unsorted/non-native rows.
This is a direct helper API integrity gap; normal SpendMap CSV import already
normalizes vendor/month and canonicalizes source line ordering. There is **no
evidence of customer exploitation**.

## Implemented boundary

`fvs_suite.spend_group_digest_r427.checked_spend_group_evidence` now snapshots
all group inputs before hashing and requires:

- R426's strict native 64-lowercase-hex source SHA-256;
- an exact built-in ASCII `[A-Z0-9]+` vendor key, up to 1,048,576 characters;
- an exact built-in month with 1–4-digit year 1–9999 and month 01–12 (Python `strftime('%Y-%m')` may omit leading year zeros on Linux);
- an exact built-in list of 1–200,000 strictly increasing distinct native
  integer physical rows within [2, 9,999,999,999], copied into a tuple.

The hash's existing domain prefix, field order, digest format and normal
imported-input semantics do not change. Invalid arguments fail closed with
fixed messages that do not disclose private CSV labels, customer paths,
amounts or provenance. The source input remains immutable; the review output
remains a *human review cue*, never fraud/compliance/approval authority.
No Decimal arithmetic, network behavior, entitlement or product release gate
was touched.

## Verification and limits

Local Linux isolated verification using this new helper and the exact R426
source-SHA guard's functional code, with synthetic values:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_spend_group_digest_r427.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_spend_group_digest_r427.py
```

**18/18 normal + 18/18 optimized passed locally** in an isolated reproduction
of the committed helper source and R426 dependency. Byte-for-byte repository
integration, the eight new real-engine integration methods, inherited suites,
and native Windows were not executed locally. The committed Ubuntu/Windows
workflow specifies the four new test commands for independent execution.

The helper does **not** establish the source SHA's authenticity or prove the
caller computed it from the same descriptor-verified CSV snapshot. It does
not protect against later disk mutation, machine compromise, or source
substitution outside the validated snapshot pipeline.

## Release / QD hold

Do not merge or deploy without independent QD review and explicit founder
approval. `release_authorized=false`. No EXEs, public download URLs,
premium artifacts, site edits or payment/compliance approvals were issued.

Next highest-impact gate: resolve GitHub Actions' pre-runner failures,
run the exact committed four R427 commands and complete six-app regression
suites on Ubuntu and Windows, then build/smoke-test real x64 executables,
Defender scans, accessibility and gated premium distribution.
