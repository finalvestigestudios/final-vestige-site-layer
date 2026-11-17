# Labs R491 — isolate Windows source-check execution until Job Object assignment

**INTERNAL / DRAFT / QD HARD HOLD.** Tracks #73. This sprint stacks on R490 draft #2835 at commit \`c11b3475e7d04fb034d35a2d33dc7a99cab80649\`; it does not target production \`main\`, modify WordPress or authorize releases.

## Why

The R490 Windows source-test runner creates \`subprocess.Popen()\` before assigning the process to its Job Object. A Python test suite could begin importing project modules or spawning descendants during that assignment interval. R491 starts the interpreter with \`-I -S\`, which disables environment-driven Python path injection and automatic site startup, and runs a minimal built-in bootstrap that **waits for one byte from a parent-owned pipe**. The parent assigns the R490 Job Object first, sends \`G\` only after successful assignment, then closes the pipe. On EOF, any other byte or custody failure the bootstrap exits without importing the test suite.

The command adapter accepts only the exact existing unittest discovery invocation with a bounded source file pattern. After the authorized handoff it runs \`site.main()\` (to make pinned site dependencies available) and then invokes the original unittest discovery under the same normal/\`-OO\` mode. Original operator stdin remains unshared; the control pipe carries only a literal token.

**Caveats:** The Windows Python interpreter and its trusted standard library still start before Job Object assignment. A compromised interpreter, unsafe DLL search path, privileged escape or native process started through a different path remains out of scope. This is a mitigation for **test-code pre-assignment execution**, not a security sandbox. Actual native Windows behavior is **not validated** until its real Windows x64 integration suite runs.

## Changed artifacts

- \`products/desktop/windows_source_start_custody_r491.py\`: strict unittest argument adapter and isolated startup handoff.
- \`products/desktop/offline_source_gate_r485.py\`: on Windows, creates a private startup pipe, assigns R490 custody, only then sends the start token; aborts/cleans up on startup or job failures. POSIX execution remains unchanged.
- \`products/desktop/tests/test_windows_source_start_custody_r491.py\`: eight cross-platform tests, including genuine subprocess execution proving correct handoff, closed/wrong token refusal, optimized mode, strict receipt, and command injection refusals.
- \`.github/workflows/desktop-source-evidence-r385.yml\`: Ubuntu/Windows normal and optimized invocation of R491 regressions.

## Local evidence and limitations

Executed on Linux with CPython in an isolated temporary fixture:

\`\`\`sh
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_windows_source_start_custody_r491.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_windows_source_start_custody_r491.py
\`\`\`

**8/8 PASS normal; 8/8 PASS -OO; compilation PASS.** The two new source/test files were compared byte-for-byte against their committed GitHub blob SHA-1 identifiers after creation. These are real local subprocess tests with synthetic fixture files; they **do not prove the modified runner works on Windows, or constitute full application-engine tests**. No Windows EXEs were built, scanned or published.

## Required QD gates and next action

1. Restore GitHub Actions runner eligibility / billing or execute the trusted full checkout on a real Windows x64 host. Existing R490 exact-head source and build jobs failed before any steps; this is not evidence that application tests fail.
2. Run R491, R490 and inherited R485-R489 regressions, then invoke the complete real six-engine source matrix in normal and optimized Python. Confirm private startup handoff and nested-job policies on Windows.
3. Build all six Windows x64 binaries and perform executable-level smoke tests, Microsoft Defender scans, SHA-256 inventory, accessibility review, entitlement and premium distribution access-control checks.
4. Keep \`release_authorized=false\`; independent QD review plus explicit founder approval are mandatory before any merge to production or live downloads.

No compliance decision is automated and no original financial data is uploaded. Decimal-safe financial values, deterministic evidence, local-first privacy and all six product tier distinctions are unchanged.
