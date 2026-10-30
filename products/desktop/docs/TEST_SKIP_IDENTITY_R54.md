# R54 — exact active and skipped regression-case provenance

**Development-only source verification.** Nothing in this change authorizes the release of Windows executables, premium downloads or unreviewed compliance decisions.

## Concrete R53 gap
The previous runner compared the *discovered* test-ID digest and total skipped count across normal and optimized Python. Two different test cases could swap which was skipped while retaining **the same discovered cases and skip count**. That could incorrectly allow an apparently matching full-suite result without exercising the same assertions.

## Fail-closed improvement
- Versioned child manifest \`fvs-unittest-provenance-v2\` retains counts and the discovered-ID SHA-256 digest, and adds \`active_ids_sha256\` and \`skipped_ids_sha256\`. All digests sort test IDs before hashing. These are identifiers, **not** sensitive failure text, skip reasons or source data.
- Rejects duplicate/unknown skipped IDs, zero active cases, and any test-named module with no active case. A whole-platform conditional skip is therefore a deliberate blocked verification, not silent success.
- The outer offline gate demands the **exact** v2 manifest and compares all fields across normal and \`-OO\` runs, catching skip-set swaps even when overall counts are unchanged. Legacy v1/malformed manifests fail closed. Source/test custody checks and all six synthetic source-engine smokes remain required.
- No financial-record changes, telemetry, payment approval automation, license keys or production edits.

## How to test on a complete trusted checkout

\`\`\`powershell
$env:PYTHONPATH="products/desktop"
python -m unittest discover -s products/desktop/tests -p test_unittest_skipped_provenance_r54.py -v
python -OO -m unittest discover -s products/desktop/tests -p test_unittest_skipped_provenance_r54.py -v
python -m unittest discover -s products/desktop/tests -p test_unittest_provenance_r53.py -v
python -m unittest discover -s products/desktop/tests -p test_offline_source_gate_r52.py -v
python products/desktop/scripts/offline_source_gate.py --report C:\fvs-private-evidence\new-r54-report.json
\`\`\`

The \`--report\` destination must be an already-existing private directory outside the checkout with a **new** filename. Preserve evidence privately. When a whole module is intentionally skipped on a platform, **do not weaken the gate to force a pass**: add a genuine platform-independent test for that module or document a separate manually verified platform-bound test and require QD to decide the release gate.

## Evidence limits

Focused synthetic tests cannot establish complete repository integration, native Windows 11 GUI behavior, packaged EXE trust, executable malware scanning, clean-machine deployment, entitlement distribution or QD approval. All six applications remain unreleased.

Tracks [Final Vestige Labs issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).
