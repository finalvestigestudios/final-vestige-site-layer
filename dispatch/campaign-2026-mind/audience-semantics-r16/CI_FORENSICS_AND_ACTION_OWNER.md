# R16 — GitHub Actions red: evidence, no speculative fix

At the **exact R15 parent SHA** `c9bf5490f2361752ab4bf390bdbf0d67563141e3`, `.github/workflows/dispatch-campaign-qa.yml` has Git blob `371a37c1334416828b708d35500268845372f9eb`. The workflow uses `ubuntu-latest`, `checkout@v4`, `setup-python@v5` Python 3.11, `setup-node@v4` Node 20, and the following actual steps:
```sh
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v
node --check dispatch/campaign-2026-mind/tools/build_previews.cjs
node dispatch/campaign-2026-mind/tools/build_previews.cjs --check
```
Three separate GitHub Actions pull-request runs are **failure**:
- [R13 #41177595807](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41177595807)
- [R14 #41181746427](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41181746427)
- [R15 #41185259100](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41185259100).

The API returns only the `local-content-safety` job with `conclusion=failure`; its `steps` are empty and fetching logs returned a **404 BlobNotFound**. Run #41185259100 started 2026-10-31 **08:35:53Z**, marked updated **08:35:57Z**, a very short four-second interval. This is consistent with an early failure *but does not establish the cause*. Do not attribute it to Python/Node versions, tests or runner allocation without a real error trace.

**Action owner / least-risk next inspection:** A GitHub repository operator with Actions UI access should open the run, check runner assignment and event logs/annotations, verify whether the checkout or runner actually initialized, distinguish platform-setup failure from a failed test command, and copy **redacted relevant step output** into Issue #174. If no steps existed, pursue GitHub Actions runner/permission/billing/queue diagnostics rather than editing the campaign tests. If steps ran, reproduce the exact failing command on Python 3.11 / Node 20 from the exact PR head before proposing an isolated fix. No shared workflow change has been authorized here.

This R16 branch adds only subscriber-reconciliation evidence and tests under `audience-semantics-r16/`. It does not modify workflows, CI settings, approvals, homepage code or publishing behavior. **Never mark CI green on local test success.**
