# R147 independent test/QA evidence — 2026-11-05 (Pacific)

## Source-of-truth consulted BEFORE development
- GitHub #174 including latest R146 and Mind #171 handoff, master campaign PR #175, QA PR #201, latest R146 PR #1154 and homepage separation PR #49.
- Authenticated WordPress Newsletter `status` and `get_settings` at **2026-11-05T22:34:58Z**; published `/focus/` page #1579 (stored editor content; modified Nov 3), `/dispatch/` page #523, Editorial Standards, public contact content, and PDF media #1737.
- Grok / Praxxis TASK-008 and dated Drive handoff **read only**, no task queue changed.
- Connected Gmail exact-terms searches returned **zero matching messages in this queried mailbox**, not universal evidence of absence, for named affiliate permission and received Fieldbook welcome. No subscriber address displayed.
- Official source review: WordPress 2026-10-06 email preview documentation, FTC CAN-SPAM guide, exact Hypnosis Live Total Focus seller page; seller claims are not independent proof.

## Reproducible independent execution
1. **Canonical master PR #175** at exact head `d57ccdba3aee8f065e143e101c2945f4f3d01647`: all eight source blobs checked against GitHub (blob SHAs 039b452b, faa207ab, aeeef34e, 89635bfb, a9dfaa45, 004d558d, 86df98ad, fd7f05e3). Native `python -m unittest discover -s dispatch/campaign-2026-mind/tests -p test_campaign.py -v`: **6/6 PASS**.
2. **R147 source** committed blob SHA `4dd39b1c23c58cea863eb3270ab040c7687478ec` and **R147 test file** blob SHA `4a05b97b341c15aa621694fd0d8345e181b44ab5` matched files independently fetched from GitHub at PR head. Native installed Node.js `v22.16.0`: `node --test test_focus_truth.cjs` **29/29 PASS, 0 FAIL**. Additional V8 direct executable test matrix **39/39 PASS** during source creation.
3. The 29 native Node tests include positive/negative UI query behaviors, stored Jetpack block vs dynamic form, strict hypothetical native evidence (consent scope, status, timestamp, audit ref), rejection of PII fields, de-duplication, and irrevocable no-send / no-merchant-link status. All inputs synthetic, not real subscriber identity events.
4. Four original R147 files fetched back from GitHub before issue posting: source, unit tests, redacted live settings snapshot, README. No changes outside `dispatch/campaign-2026-mind/r147/`.

## What tests cannot establish
The stored WordPress Focus source definitely has an overly permissive *gift display* conditional. **Neither an actual anonymous browser success panel run nor a bogus emitted analytics event, provider subscriber status, actual email receipt, real PDF retrieval/page count, live checkout, or sale was tested.** No provider confirmation events were available for audit. `confirmed_signup`, paid conversion counts and net revenue per 1,000 qualified humans remain **UNKNOWN / NOT COMPUTABLE**.

## Release gate
All 6 campaign messages `HOLD_UNSENT`; #03 Zen12 Premium / #05 Hypnosis Live **Total Focus** also `HOLD_MERCHANT`. Confirmed native consent, publisher-valid postal address, working actual unsubscribe, preview, named affiliate email rights/current terms/guide live, paid settlement and founder **final send** approval not established. No WordPress write, test email, draft post, scheduled send, list import, affiliate link, new measurement script, paid tool or social activity.
