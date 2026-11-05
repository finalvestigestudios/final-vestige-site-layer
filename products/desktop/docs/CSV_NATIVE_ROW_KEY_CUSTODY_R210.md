# Labs R210 — native row-key custody in audit CSV exports (DRAFT / HARD HOLD)

Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). This sprint is an isolated feature branch stacked on [R209 draft #1095](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1095), from immutable parent `095157e0e2bed234027ec52d4ef591ebb91f7ee6`. No production/main merge or release authorization.

## Reproduced issue and fix

R209 verified that declared CSV fields appeared in the rendered-row dictionary, but it trusted mapping keys while doing so. A `str` subclass can override `__hash__` and `__eq__` to compare equal to `source_row` despite its *actual source label* being something else. Python dictionary membership then reports that `source_row` exists, and `DictWriter` may publish the impostor value as if it were genuine provenance. Also, a custom mapping may return duplicate `.items()` keys; comprehension silently keeps the last value.

R210 snapshots the iterable of mapping items before sanitization, explicitly rejects non-mapping rows, requires `type(key) is str` for every key, and rejects duplicate items before constructing the rendered row. Errors are static and do not print financial names or values. Complete ordinary dictionaries, mapping proxies, Decimal-to-text conversion through the provided sanitizer, explicit blanks, and the preexisting sanitization of *all* native-string extras continue working. Existing published evidence remains immutable; failed staging is deleted. This only hardens report-output custody. It does not authorize payment or provide compliance/legal determinations.

## Measured local evidence

- Linux CPython 3.13.5, synthetic ephemeral fixtures; no customer data, remote service or premium files.
- **Red phase against exact committed R209 writer** Git blob `8057284fa314f4ae0e1008f9f6a84e91fcd5a001`: new 16-case test file produced **9 failures + 2 errors**; demonstrates forged `source_row`, duplicated entries, and invalid-key acceptance.
- **Green phase against exact proposed R210 writer** blob `d456cec2d2e0024d4cf33807c92a1e31205b9cd5`: **16/16 passing normal**, **16/16 passing `python -OO`**, for **32/32 focused executions**. Two files compile successfully. The tested local sources were independently checked against committed Git blob hashes.
- Test source blob: `4061bceca47aa054a6de5952a59804746248692b`. Tests validate forged equality/hash keys, non-text keys, duplicate custom mapping items, 128-row late failure and cleanup, existing-evidence preservation, privacy-safe exceptions, mapping-proxy compatibility, Decimal output, and BOM.
- Desktop CI configuration adds R210 16-test normal and `-OO` runs to **both** Ubuntu and Windows jobs, with explicit Windows exit checks. Workflow edit is not hosted execution evidence.

Local invocation:
```sh
PYTHONPATH=/mnt/data/labs-r210 PYTHONWARNINGS=error python -m unittest discover -s /mnt/data/labs-r210/tests -p test_atomic_row_key_custody_r210.py
PYTHONPATH=/mnt/data/labs-r210 PYTHONWARNINGS=error python -OO -m unittest discover -s /mnt/data/labs-r210/tests -p test_atomic_row_key_custody_r210.py
python -m py_compile /mnt/data/labs-r210/fvs_suite/atomic_reports.py /mnt/data/labs-r210/tests/test_atomic_row_key_custody_r210.py
```

**Limits:** Isolated reconstruction of the exact writer plus R210 tests, not an authenticated full-repository checkout. The inherited financial/Policy Delta suites, real six-engine end-to-end exports and native Windows binaries were **not** run locally. GitHub-hosted CI has repeatedly failed with no available job steps; root cause unconfirmed. No distribution or QA sign-off is claimed.

## Next decisive acceptance

1. Owner restores runner allocation/Actions access and reruns **unchanged R210 exact HEAD** on Ubuntu and Windows, witnessing complete source suite plus all six report/smoke flows. Ensure newly strict row labels do not break ordinary producer output.
2. Private Windows x64 builds, checksums, Defender scanning and real Win11 smoke/keyboard/NVDA/high-DPI acceptance for all six distinct apps.
3. Authenticate/gate premium GrantAudit and ProcureGuard binaries, review code signing or clear unsigned labeling, obtain independent QD review and explicit founder release approval before any main merge or WordPress publication.

**Release hold:** LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, and ProcureGuard Studio Pro remain unreleased. No public EXE, invented download, ungated premium link, production edit or payment/compliance automation.
