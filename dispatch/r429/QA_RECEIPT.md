# R429 pre-commit source verification

Verified original PR #175 HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647` is still OPEN/DRAFT, and source hashes matched the eight-file local original master test run. Fresh native Python 3.13.5 `unittest discover` performed before building these specimens: **6/6 PASS**. Original suite has limited offline assertions only. The supplied original files were from a previous verified local package; all eight blob SHAs were independently rechecked against the live GitHub master HEAD during this run.

R429 generator was exercised independently before commit: **53 synthetic source/content/release checks PASS**. Includes six deliberately altered preheaders correctly rejected. Native Node test file and Gutenberg block saved-file parity will be run after GitHub commit if executable source is locally available; do NOT claim them run merely because they are committed. No browser, WordPress editor, real email, native unsubscribe or paid conversion was tested. Release remains HOLD_UNSENT.

## Final-source validation following QA correction

A committed-test regex was found to use a double-escaped word boundary, making the active-element test weaker than intended. Corrected in commit `176f59391427d7685cc240eac23bab44692ab4f8`; the R429 source specimens themselves were not modified. Independently refetched **12/12 R429 files** plus **7/7 inherited canonical source files** at the corrected branch HEAD; **57/57 explicit source/CTA/legal/safety/tampering assertions passed** in the V8 validation harness. The **exact committed `test_gutenberg.cjs` source** was then executed in V8 with narrow Node-compatible `fs`, `path`, and `assert` shims, producing **45/45 passed assertions**. This is *not native Node*, GitHub Actions, browser rendering or a live WordPress email test. Latest read-only newsletter counts 3 / 3 / 2 are categorical snapshots, **not** an eligible audience list.

No native WordPress Preview was performed; the founder has not approved a test email. Named Inspire3 EMAIL rights and issue 03/05 live buyer guides remain unavailable. **Do not interpret tests as release approval.**
