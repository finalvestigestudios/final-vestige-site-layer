# R78 — Policy Delta Desk non-ASCII whitespace visibility

**Status:** Draft engineering change stacked on R77. Not a release, legal
interpretation, compliance determination, or distribution authorization.

## Defect and behavior

A nonbreaking space (U+00A0), narrow nonbreaking space (U+202F), figure space
(U+2007), thin space (U+2009), ideographic space (U+3000), and other non-ASCII
Unicode `Zs` spacing separators can look the same as an ASCII space in plain
text. Previously two different policies could therefore have an accurate SHA-256
and diff hunk but appear visually identical to a reviewer.

The source-line display now writes each non-ASCII `Zs` as a deterministic
`\\uXXXX` escape, while retaining ASCII spaces normally. It also retains
R76/R77 literal-backslash, tab, CR, format-character and variation-selector
handling. This applies to added, removed and context lines, **not** metadata
and not original source files. It does not claim to detect all Unicode
confusables; reviewers must examine original evidence as needed.

## Reproduce and test

From `products/desktop` on Linux with Python 3.13.5:

```sh
PYTHONPATH=. python -W error -m unittest discover -s tests -p 'test_policy_spacing_r78.py' -v
PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p 'test_policy_spacing_r78.py' -v
python -m compileall -q fvs_suite/policy_diff.py tests/test_policy_spacing_r78.py
```

Before the patch, the exact R77 source failed 29 assertions/subtests in the
20-method R78 suite. With this patch, **20/20 passed** normally and **20/20
passed** under `-OO`; compilation passed. Tests use real local synthetic TXT
files, descriptor-owned snapshots, actual atomic report publication, SHA-256
checks and immutable originals. They also check no-overwrite fail-closed
behavior, unsafe bidi rejection, UTF-8 validation, and existing CR/tab rules.

This verification is limited to an isolated reconstructed workspace containing
**exact GitHub source blobs** of `policy_diff.py`, `csv_snapshot.py`, and
`atomic_text.py`, plus the exact committed R78 test file. It is **not** a
complete repository test run or native Windows executable smoke. The production
repository, public website, binaries, premium access controls, Decimal money
logic and reviewer decision rules are unchanged.

## Release hold

GitHub Actions runner-start issue #75 prevents authoritative Linux and Windows
jobs from recording test steps. Restore a minimal hosted runner job, then run
full normal and optimized suites, all six genuine Windows x64 EXE smokes,
accessibility/security/AV and premium entitlement verification. Obtain
independent QD and founder approval before any merge or publishing.
