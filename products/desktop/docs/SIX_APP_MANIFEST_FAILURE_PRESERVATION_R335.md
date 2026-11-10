# Labs R335 — fail-closed manifest retention after ambiguous publication

**Issue #73 · DRAFT · QD + founder approval HARD HOLD · no production branch / WordPress / premium distribution changes**

## Defect: post-link check→unlink race

`build_inventory.py` exclusively publishes the deterministic six-application `SHA256SUMS.txt` through a same-filesystem hardlink. On a failure after the link was created, an older `finally` block called `target.lstat()`, compared `st_dev/st_ino` to the original staged inode, then independently called `target.unlink()`. A competing local writer could swap another file into the `SHA256SUMS.txt` pathname **between those two operations**, so an attempted "safe rollback" could delete a foreign file. An injected `os.link()` wrapper could also perform a real hardlink and then report failure, making post-publication state ambiguous. Inode comparison is not an atomic conditional unlink.

## R335 change and conservative contract

- Remove only the **post-publication target rollback unlink**; retain the initial exclusive hardlink, pre-publication stage verification, post-link inode comparison, exact six-candidate fingerprints and postpublication gate verification.
- When a build fails after a successful/ambiguous link, a `SHA256SUMS.txt` file **may remain**; it is **failed-build evidence, not approval**. No subsequent build may overwrite it. An operator must inspect the failure and explicitly retire the candidate directory/manifest before retrying. Never distribute based on the mere presence of the inventory.
- Pre-link failures continue to leave no published inventory; the existing best-effort private staging-file cleanup is unchanged. This sprint does **not** claim all possible staging-path adversarial races are eliminated.
- Reconcile old R40, R243, R244 tests that required automatic postpublication deletion; preserve their prelink, privacy, interrupted-operation and foreign replacement assertions. New `test_inventory_no_rollback_r335.py` includes 10 synthetic fault-injection methods covering post-link I/O failures, exceptions, interrupts, retained canonical content, foreign replacement (regular/symlink), no target unlink attempt, prelink rejection, and explicit-retry hold.
- CI runs R335 in normal and optimized Python on both Ubuntu source-tests and private Windows packaging jobs. **No executable is built or distributed by this change.**

## Acceptance and proof boundary

Run locally with the entire repository available:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_inventory_no_rollback_r335.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_inventory_no_rollback_r335.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_inventory_*r24*.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_build_inventory_r40.py'
```

Do not describe these tests as passing until executed. Previously, hosted Actions failed before the Ubuntu/Windows steps ran; GitHub runner/billing eligibility needs owner inspection. Full repository tests, genuine premium AES-GCM integrations, Windows 11 x64 smoke, SHA256 evidence, malware scan, keyboard/accessibility, premium entitlement gating, and independent QD/founder authorization are still required.

## Release hold

Six applications remain **unreleased**. No downloads or premium payloads may be published from a failed or unreviewed build. Treat retained evidence as potentially contaminated, and use a **fresh clean staging directory** after reviewing an ambiguous failure.
