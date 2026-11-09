# R230 independent reproducibility

Source: authenticated read-only WordPress page 1579 inline gift JS observed 2026-11-09 10:35 UTC; companion settings/status. This package neither runs on the live site nor handles subscriber identities.

Native Node locally executed:
```
node dispatch/r230/test_live_focus_gift.cjs
LIVE SCRIPT REPRODUCTION: 10/10 passed; untrusted subscribe query values reveal the gift UI; NOT proof of subscriber confirmation.
node dispatch/r230/test_focus_measurement.cjs
OFFLINE EVIDENCE CONTRACT: 24/24 passed; no positive signup can be asserted by self-supplied fixtures.
```
The first script uses Node `vm` and a mocked DOM—not a real browser, no true Jetpack subscription/confirmation, no received email. The second rejects all unauthenticated synthetic positive consent/commerce claims and is intentionally **not a real provider integration**. Original six-issue Python suite was read at exact current parent R229 head (manifest and six guard tests) but **not executed in a native full private checkout**: local runtime lacks the complete repository and DNS cannot reach `raw.githubusercontent.com`. Therefore NO claim of native original suite pass. No CI or mobile inbox render.

Reviewed read-only: #174 latest comments, #171, #129, #820, PR #201, PR #1731, /dispatch/, /focus/, Editorial Standards, Jetpack status/settings, Grok TASK-008. Current QA concerns are independent of frozen homepage PR #49. Source links, statuses and actions in FINDINGS_AND_RELEASE_HOLD.md.

**Release decision:** Every newsletter HOLD_UNSENT; commercial Issues 03 and 05 HOLD_MERCHANT. No emails, test email, signup, site updates, affiliate/earning links, list import, production tracking or spending.