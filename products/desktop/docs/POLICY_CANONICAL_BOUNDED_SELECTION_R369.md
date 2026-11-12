# R369 — Bound Policy Delta Desk NFC-only audit citations

**Issue:** #73. **Status:** DRAFT / HOLD. This is source-level review evidence, **not** a legal determination, approved release, native Windows binary, or published download.

## Previously observed gap

`fvs_suite.policy_canonical.render_local_canonical_evidence` accumulated one full tuple for **every** unambiguous changed NFC-equivalent source pair, then sorted all of them to display only 16. With thousands of candidate rows this duplicated all source-text references in an unnecessary candidate list (independently of the upstream line-group indexes). Unicode codepoint formatting was already limited to the displayed 16.

## R369 source change

- `_earliest_canonical_pairs` counts **all** valid changed unambiguous pairs, but retains at most **16** tuples selected by `(hunk number, physical before line, physical after line)`.
- Uses deterministic ordered insertion; randomized Python set intersection order cannot determine which human-review citations are displayed.
- Counts excluded candidates precisely for the existing `+N omitted` disclosure. **Ambiguous duplicate NFC-folded rows, unchanged pairs, NFKC-only pairs, and nonmatching rows** are not eligible.
- Whole-collection `_verified_canonical_hunks` preflight still executes **before selection**; invalid direct caller source coordinates, unsafe subclasses or hostile dictionary keys suppress **all** supplemental citations. Long but otherwise valid lines remain uncitable while their physical coordinates are checked.
- Original policy documents, their SHA-256 provenance, human review wording and source evidence are not modified. No financial money arithmetic, licensing, vault, WordPress, binary, or production changes.

The bounded selection list **does not** bound the upstream parsed hunk indexes: this sprint only fixes avoidable candidate tuple retention. A separate resource-envelope review remains appropriate.

## Concrete tests and provenance

- New exact [23-method synthetic regression module](../tests/test_policy_canonical_bounded_r369.py): 5,000 physical rows; count/first-16/overflow; minimal formatting invocation count; 20 hunks; randomized normalized-key insertion; reverse physical coordinates; output/source privacy; Unicode codepoint details; ambiguous lines; unchanged/NFKC-only exclusions; invalid late hunk fail-closed; overlong lines; human-review language and legacy full-sort parity.
- Linux Python **3.13.5**: **23/23 PASS** standard with `-W error`; **23/23 PASS** `-OO -W error` = **46 focused executions**. Exact local source Git blob SHA `fdcb101f7b72a3ee8ef991b911f499cc1e069603` and test blob SHA `cbfcecbb0c9c86561124cbd19e7ca1cc8baf5567` match this feature branch's committed GitHub blobs.
- Four `PYTHONHASHSEED` settings `0,1,42,369` produced identical SHA-256 `dbe5d741ba8e881a97b3c820a4a7217cf5071c7596ce00b915a9d7d9cb022a94` for a synthetic 5,000-pair report. Scope: **Linux locally executed**, not GitHub Actions, native Windows or production financial data.
- In the 5,000-candidate test, bounded candidate retention is **16 tuples rather than 5,000** (99.68% fewer retained candidate tuples), while reporting **4,984 omissions**. This is not a whole-application memory benchmark.

Reproduce against checked-out branch root:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_policy_canonical_bounded_r369.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_policy_canonical_bounded_r369.py'
```

## Mandatory gates and unresolved release blockers

Both `source-tests` (Ubuntu) and `windows-build` run the new module normal and optimized **before source gate / packaging** in `.github/workflows/desktop-build.yml`. The prior R368 exact-head GitHub Actions run #43145405378 reported both jobs **failure with `steps=null`**, so the actual runner/infrastructure cause remains unverified. Local passing tests do not unblock packaging.

Still required: running the exact-head inherited full desktop source suite, 22 genuine AES-GCM cases, both hosted OS gates, six separate Windows 11 x64 builds/PE and actual launcher smoke, Defender scan, keyboard/screen-reader accessibility, SHA256 release receipts, protected premium entitlement/distribution and independent QD plus founder approval. **No public or premium downloads are authorized by R369.**

Smallest owner action: open GitHub Actions failed-job check annotations and check Actions billing/spend limits, hosted runner availability and workflow permissions; restore actual job steps and rerun the draft exact head. Do not merge this stacked draft or publish artifacts until acceptance gates and QD/founder review pass.
