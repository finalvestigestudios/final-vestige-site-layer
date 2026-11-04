# Labs R195 — SpendMap source output custody (DRAFT / RELEASE HARD HOLD)

Issue #73; parent: R194 draft PR #995 at immutable commit 50a60cbe6a140ed9a428942595f2031f7296900c. No production changes or releases. Six applications remain unreleased.

## Reproduced vulnerability and fix

R194 validated all financial source records before the first yield, but returned privately snapshotted source dictionaries as MUTABLE objects. A direct API consumer could rewrite a successful row's physical line, vendor, source amount, date, or add an apparent payment approval AFTER validation, while the separately parsed Decimal amount and source hash were unchanged. Furthermore, unused extra columns could smuggle non-string mutable/hostile objects into the report.

R195 returns read-only MappingProxyType views over privately copied native dictionaries, preserving Mapping access, read-only get/iteration, dict(record) conversion, row order, original vendor labels, Decimal values, and R194 semantic atomicity. It also rejects every non-native-str source column value, including unused extras, before parser callbacks. These checks never invoke suspect object methods; required-field diagnostic messages remain intact. Ordinary extra CSV text columns are retained.

**Compatibility:** The direct helper already promised Mapping[str, str], not a mutable dict. An extension requiring its own writable copy must call dict(record). Native CSV readers should produce plain string cells. Object-valued extra columns now fail closed. Neither a mapping proxy nor source SHA-256 is proof of filesystem authenticity; the descriptor-verified snapshot remains necessary. No legal/payment approval is automated.

## Local reproducible evidence (November 4, 2026; CPython 3.13.5 on Linux)

- Exact original R194 source blob: 52ec67b5fcd7917b81f5035f19d07fdc0337db4c.
- New 29-regression suite against unchanged R194 source: 29 run, 26 expected failures (red baseline).
- Patched source Git blob: 5d3321cb56f6fff08313fea28e9368d132ee049e.
- New test Git blob: 78efdb50187f1d9199643a2b07453cec8c120af9.
- Normal Python: 29/29 PASS. Optimized -OO: 29/29 PASS. **58/58 executed; zero skips.**
- Python compilation: PASS for source and tests.
- 200,000 synthetic rows: 200,000 yielded, preserved physical line 2 through 200001, 2.054 seconds local, maximum process RSS 263,684 KiB including fixtures.
- Test command from repository root: PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_spend_output_custody_r195.py'; rerun with python -OO.
- Scope strictly isolated exact-blob source and synthetic tests. The inherited suite, full-repository integration, hosted Ubuntu/Windows CI, Windows EXE build, Defender/EDR, signing and physical accessibility have NOT been verified.

## QD and distribution hard hold

Remain draft, stacked on R194, not production/main. Do not merge, publish, label any executable ready, expose unrestricted premium files or invent download URLs. Independent QD review and founder authorization remain mandatory.

**Next highest-impact step:** Restore GitHub Actions allocation; run complete inherited source regressions and the 14 outstanding Policy Delta real-file integration cases on both runners. Privately build and smoke-test six Windows x64 executables with SHA-256 manifests before any distribution. Owner should inspect Actions billing, usage permissions, and runner provisioning because recent jobs completed with zero steps.