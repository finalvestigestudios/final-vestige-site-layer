# R159 — authentic Family Reunification Card review snapshot (DRAFT / HARD HOLD)

**Ownership:** Preparedness Archive Issue #136 only. Cross-reference business priority #820 and charter #818. **Parent:** R158 PR #1195 at `069c2a9757850b92b17b104c0ab2ef436ee3c9c5`. No public publishing, CMS/WordPress/navigation/analytics/merchant changes, merge or QD approval.

## Actual change

Unlike R158's in-memory proposal, R159 stores the **authentic source-derived** Family Reunification Card HTML and metadata in the quarantined directory `preparedness/review/r159/`, **outside** `preparedness/content/`. This is **review input only**, not a WordPress-ready or publishable build artifact. The native builder must separately render and review any eventual approved draft; no unreviewed source is ever treated as safe.

Original body Git blob `be8698ac5d020476ff649d85813810e2000c6f98` (19,145 characters) and metadata blob `47da1e7e20e39f0ea85e26d54a8d58301f6e0a15` were fetched at the exact parent and authenticated by the GitHub connector. Exactly **five R158 HTML text replacements and two metadata claim corrections** were applied to create the quarantined review snapshots; the resulting body has 19,345 characters. The original input files were not edited.

The correction narrows unsupported privacy/storage guarantees, overbroad SMS-versus-voice advice, inaccurate no-JavaScript feature instructions, unverified Ready.gov privacy claims, and unsupported Colorado school-pickup attribution. These are **editorial proposals**, not findings that any remaining wording is independently safe.

**Conservation checks on actual source snapshots:** 16 original ordered citation tokens retained; 11 source-use interpretations retained verbatim; identical HTML element sequence and embedded CSS/JS; no reduction in body length; metadata `publish=draft` and `safety_review.state=pending` retained. The six sources previously inaccessible to automated retrieval are not deemed dead; Colorado and NCMEC scope discrepancies remain for qualified review. No R158 proposal is automatically approved, even when structurally correct.

## New deterministic audit and tests

`preparedness/tools/r159_stage_review.py` pins the exact R158 gate Git blob `2efbf2d20ed0c5f31b1e00db949a1b3ebf33ab1f`, plus frozen R151 35-article metadata manifest Git blob `9cf386519eda970209ff6be4ff0243661cd9d996`. It independently recomputes R158's output from pinned source inputs and rejects any snapshot that differs byte-for-byte; rejects altered source use, citation order, publication/safety status or substantial reading-depth loss. It also performs a 35-body/35-metadata census, unique-route check, draft-status check and metadata Git blob identity check in a **trusted full repository checkout**.

The audit always reports `DRAFT_HARD_HOLD` or `INVALID_HARD_HOLD` and always exits **2**. Neither result is a safety, medical, source, QD, conversion, or founder approval.

Local tests: **71/71 isolated Python unit tests passed**, including 64 independent malicious candidate mutations, forged publication state, lost source relationships, missing manifest and symlink checks. Python compilation passed. Commit blob identities must match the locally tested code and tests. These are isolated tests; the native complete-repository audit, build, complete 35-article suite, WordPress renderer, mobile screen reader, browser privacy and print tests were **not executed**, because the local GitHub DNS lookup prevents an authenticated clone. The browser-script inspection also cannot establish whether extensions, WordPress, shared devices or printing services retain form entries.

Required trusted-checkout commands:

```sh
python -I -m unittest discover -s preparedness/tests -p 'test_r159_stage_review.py' -v
python -I preparedness/tools/r159_stage_review.py --repo . # exit 2 expected; inspect DRAFT_HARD_HOLD vs INVALID_HARD_HOLD
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

All 35 original instructional articles remain DRAFT / HOLD. Source docket retains **75 pending tasks**: eight Historical Food substitutions, eleven Family Card source relationships, four source-interpretation changes and 52 other tool-source tasks. No duplicate URL/source interpretations are silently merged, and no founder/qualified-human release gate is bypassed.

## Coordination and conversion-first staging

Seven Claude clusters compared to exact R157 heads on 2026-11-05: **7/7 identical** (Start Here `2122d856`, Shelter `5daeaf2d`, Food `f911ff7a`, Health `d5ef5baf`, Historical Food `67e116e5`, Historical Home `7504a5f0`, Historical Field `4e5caf81`). Independent draft QA PR #157 (`7d1ae6b8`), fixture PR #169 (`e9cd7766`) and its stacked #973 (`4d40996a`), and homepage PRs #49/#604 remain untouched. No automated merge or new GitHub Actions spending.

Only proposed intent match: families with school-age children planning emergency pickup/reunification → **free Household Emergency Plan** (essential guidance ungated) → optional **free Family Reunification Card** (current source/print/privacy HOLD) → a rights-cleared existing **paid** Preparedness pack **only after independently verified**. No such matching purchasable SKU, merchant delivery/refund evidence or confirmed Grok Preparedness asset ID has been authenticated. No paid CTA or UTM link is active. TASK-008 and dated handoff are read-only and Grok/Praxxis retain ownership.

| OFFER → STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Existing paid Preparedness pack → purchase | SKU/rights/pricing/merchant fulfillment not authenticated | Read-only product, guest/mobile checkout, digital fulfillment, fees/refund audit | HOLD; no verified paid orders | Commerce / Claude |
| Household Emergency Plan → free visitor | Qualified source/safety, QD and native build incomplete | Preserve free access, run trusted build and staged page checks | DRAFT; no clearance | Preparedness / QA |
| Free guide → optional Family Card | 11 pending source mappings; privacy claims and print QA | Review R159 authentic candidate and test 360/390/768/1440 px, JS disabled, actual printing and network privacy | 71 isolated tests; authentic browser NOT VERIFIED | Preparedness / independent QA |
| Grok asset → approved destination | No authenticated published Preparedness asset ID/CTA placement/URL | Read TASK-008 inventory with Praxxis; approve exact compliant destination before use | UNKNOWN; no attributed traffic claimed | Grok / Praxxis |
| Verified order → realized net per 1,000 qualified sessions | No reconciled merchant orders, fees, refunds, qualified session denominator | Reuse #820 privacy contract and 7/30-day cohorts; missing fields remain null | NOT COMPUTABLE | Commerce / Growth |

**DRAFT / HARD HOLD:** leave all source opinions as pending, do not publish a staging HTML file, do not send emails/posts, do not modify production, do not create new products or falsely claim QD PASS.
