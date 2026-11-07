# Labs R253 — Six-app Generate report destination custody

**2026-11-07 UTC · DRAFT / independent QD + founder HARD HOLD.** Stacked on R252 head `8ad2846fefafadf28e025bef64a813505f5e71f7`, not production `main`. No live site changes, binaries, artifacts, licenses or premium links were published.

## Reviewed-code defect

R251 checked that returned paths were native nonempty regular files, but it did **not** check that they were the intended *product's* files or were inside the *operator-selected* output folder. A faulty engine/plug-in return value containing an unrelated existing CSV could trigger an apparent **success**. For premium Generate, the first returned path would then become the implicit review target, even without the mandatory evidence manifest and other reports. A symlinked bundle directory or two separate names for one hardlinked evidence file also lacked a fail-closed boundary here.

## Change

- `fvs_suite/report_completion.py` now accepts paired `folder` and `app_id` context. Its prior direct-call signature without either remains available for isolated original tests; the production GUI always supplies both. Only native built-in paths are trusted. Output files must be regular and nonempty; duplicate leaf paths and positive-inode hardlink aliases are rejected. The selected output directory must exist and not itself be a symlink.
- For **LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk**, require exactly one report, directly inside the selected directory, with the corresponding engine-defined stem, timestamp and `.csv` or `.txt` extension.
- For **GrantAudit Studio Pro**, require exactly the ordered two CSVs plus evidence manifest together under one directly nested `grant-evidence-YYYYMMDDTHHMMSSZ-<32 hex>` directory. For **ProcureGuard Studio Pro**, require the one three-way CSV plus manifest under its analogous `procurement-evidence-` directory. The bundle itself cannot be a symlink.
- `fvs_suite/app.py` passes the selected folder and product into this check **before** success messages or automatically selecting the premium exception-review report. Existing redacted fail/inspect-before-retry behavior remains unchanged; outputs are never erased, retried, or submitted elsewhere.
- `tests/test_report_completion_r251.py` GUI fixtures were made representative of real product filename and premium bundle output contracts so inherited acceptance checks remain meaningful.
- `tests/test_report_destination_custody_r253.py` adds **26 filesystem regression methods** with four free/six-app acceptance paths, bundle completeness, cross-folder/wrong-product denial, symlink/hardlink, duplicate/missing/nonregular reports, error privacy, no source mutation, legacy helper compatibility.

## Local evidence, limits and release hold

The **exact committed** new report helper and regression file matched Linux-executed source Git blobs:
- `report_completion.py`: `bb16170c8408ce0b5e281699939f2f44c61ed143`
- `test_report_destination_custody_r253.py`: `2001f8ab27e3a8d32c7f7ba224f722f7ad4a0fd3`

Executed in isolated Linux Python against those exact source files:

```sh
PYTHONPATH=<R253-isolated-products-desktop> python -W error -m unittest discover -s <R253-isolated-products-desktop>/tests -p 'test_report_destination_custody_r253.py'
PYTHONPATH=<R253-isolated-products-desktop> python -OO -W error -m unittest discover -s <R253-isolated-products-desktop>/tests -p 'test_report_destination_custody_r253.py'
python -m compileall -q <R253-isolated-products-desktop>/fvs_suite <R253-isolated-products-desktop>/tests
```

**26/26 PASS normal, 26/26 PASS -OO, 0 skips; 52 focused test-method executions; compilation PASS.** Synthetic evidence only. These results **do not** establish complete repository/Tk integration, Windows 11 UI, actual generated CSV/manifest content attestations, private native Windows packaging or hosted CI. Updated inherited R251 GUI fixtures are committed but not executed against the full repository locally.

**Limitations:** This is a *post-write snapshot*, not an atomic provenance proof: a privileged process could replace files after checks. Native Windows may report `st_ino=0`; in that case hardlink identity cannot be verified by this helper. Existing engine outputs are still validated separately by source snapshot and bundle publisher. Rejecting an output directory that is itself a symlink is intentional and can require the operator to select its underlying actual directory. No security or release certification is claimed.

## QD and Windows release prerequisites

1. Confirm real Windows 11 x64 runs for all six engines including both GrantAudit paths (legacy and linked allocations), both premium manifest packages, output folder selection and errors; test Windows inode behavior, hardlink/symlink and keyboard/screen-reader navigation.
2. Restore GitHub Actions and run the unchanged R253 head: full source tests normal and `-OO`, six-engine demo smoke, Windows private builds, checksums, Defender and workflow custody checks. Previous R252 [run #42353806866](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42353806866) ended with both Ubuntu and Windows jobs failed and `steps=null` (no build or test verified). Owner should inspect Actions billing/usage, permissions and hosted runners; no root cause has been established.
3. Verify artifact manifest bytes, provenance, no private data leakage, accessibility and premium access controls; obtain **independent QD + founder authorization** before any release. No production merges, public executables or unrestricted paid links.

**Next highest-impact step:** Restore hosted CI, execute the full repository regression suite and native Win11 x64 smoke for these six exact destination schemas, then privately package and checksum each application. Keep all six **UNRELEASED** pending QD.
